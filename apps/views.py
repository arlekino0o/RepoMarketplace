from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from apps.products.models import Category, Repository
from .serializers import CategorySerializer, ProductSerializer


class CategoryListView(generics.ListAPIView):
    """API-эндпоинт для получения списка всех категорий"""
    queryset = Category.objects.all()
    serializer_serializer = CategorySerializer
    #можно явно разрешить просмотр каталога всем:
    permission_classes = [] 


class ProductListView(generics.ListAPIView):
    """API-эндпоинт для получения списка товаров с фильтрацией по категории"""
    queryset = Repository.objects.all()
    serializer_class = ProductSerializer
    permission_classes = []
    
    #Django REST Framework
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'seller']


class ProductDetailView(generics.RetrieveAPIView):
    """API-эндпоинт для просмотра конкретного товара по ID"""
    queryset = Repository.objects.all()
    serializer_class = ProductSerializer
    permission_classes = []