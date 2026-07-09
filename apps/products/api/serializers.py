from rest_framework import serializers
from apps.products.models import Category, Repository


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий товаров"""
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для полноценного вывода товаров в каталоге"""
    category = CategorySerializer(read_only=True)
    seller = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Repository
        fields = [
            'id', 
            'title', 
            'description', 
            'price', 
            'stock', 
            'image', 
            'category', 
            'seller', 
            'created_at'
        ]