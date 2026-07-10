from django.urls import path
from .views import CategoryListView, ProductListView, ProductDetailView

app_name = 'products_api'

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]
