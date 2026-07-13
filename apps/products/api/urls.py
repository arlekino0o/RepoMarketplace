from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ProductVersionViewSet, ProductReviewViewSet, \
    AddProductVersionAPIView

app_name = 'products-api'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='list')
router.register(r'versions', ProductVersionViewSet, basename='version')

urlpatterns = [
    path('products/<slug:product_slug>/add-version/', AddProductVersionAPIView.as_view(), name='api_add_version'),
    path('products/<int:product_id>/reviews/', ProductReviewViewSet.as_view({
            'get': 'list',
            'post': 'create'
        }), name='product-reviews'),
    path('', include(router.urls)),
]
