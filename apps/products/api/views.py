from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from apps.products.models import Category, Repository
from .serializers import CategorySerializer, ProductSerializer


class CategoryListView(generics.ListAPIView):
    """API-эндпоинт для получения списка всех категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer  
    permission_classes = [] 


class ProductListView(generics.ListAPIView):
    """API-эндпоинт для получения списка товаров с фильтрацией по категории"""
    queryset = Repository.objects.all()
    serializer_class = ProductSerializer
    permission_classes = []
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['categories', 'seller']


class ProductDetailView(generics.RetrieveAPIView):
    """API-эндпоинт для просмотра конкретного товара по ID"""
    queryset = Repository.objects.all()
    serializer_class = ProductSerializer
    permission_classes = []