from django.http import FileResponse
from rest_framework import viewsets, permissions, serializers, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products.models import Category, Product, ProductVersion, ProductReview
from .serializers import (
    CategorySerializer,
    ProductReadSerializer,
    ProductWriteSerializer,
    ProductVersionSerializer, ProductReviewWriteSerializer, ProductReviewReadSerializer, ProductVersionUploadSerializer
)
from .permissions import IsSellerOrReadOnly
from django.db.models import Q


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).prefetch_related('versions')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsSellerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'seller', 'license_type']
    search_fields = ['title', 'description', 'tech_stack']
    serializer_class = ProductReadSerializer
    lookup_field = 'slug'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ProductReadSerializer
        return ProductWriteSerializer

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        slug = self.request.query_params.get('slug')
        if slug is not None:
            queryset = queryset.filter(slug=slug)
        return queryset

    @action(
        detail=True,
        methods=['get'],
        url_path='download',
        permission_classes=[permissions.IsAuthenticated]
    )
    def download(self, request, slug=None):
        product = self.get_object()

        is_seller = product.seller == request.user
        is_free = product.price == 0
        is_purchased = True

        if not (is_seller or is_purchased or is_free):
            return Response(
                {"error": "Для скачивания необходимо приобрести этот товар."},
                status=status.HTTP_403_FORBIDDEN
            )

        requested_version = request.query_params.get('version')

        if requested_version:
            version_obj = product.versions.filter(version_number=requested_version).first()
        else:
            version_obj = product.versions.first()

        if not version_obj or not version_obj.source_archive:
            return Response(
                {"error": "Файлы для указанной версии продукта не найдены на сервере."},
                status=status.HTTP_404_NOT_FOUND
            )

        product.download_count += 1
        product.save(update_fields=['download_count'])

        response = FileResponse(version_obj.source_archive.open('rb'), as_attachment=True)
        return response

class ProductVersionViewSet(viewsets.ModelViewSet):
    queryset = ProductVersion.objects.all()
    serializer_class = ProductVersionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSellerOrReadOnly]

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        if product.seller != self.request.user:
            raise serializers.ValidationError("Вы можете добавлять версии только к своим товарам.")
        serializer.save()

class ProductReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductReviewWriteSerializer
        return ProductReviewReadSerializer

    def get_queryset(self):
        return ProductReview.objects.filter(product_id=self.kwargs['product_id']).select_related('user')

    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        serializer.save(user=self.request.user, product_id=product_id)


class AddProductVersionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = ProductVersionSerializer

    def post(self, request, product_slug):
        product = get_object_or_404(Product, slug=product_slug, is_active=True)

        if product.seller != request.user:
            return Response(
                {"error": "Вы не являетесь автором этого продукта."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductVersionUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(
                {"message": "Новая версия успешно выпущена!"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)