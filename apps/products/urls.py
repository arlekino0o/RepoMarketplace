from django.urls import path
from .views import ProductListView, ProductCreateView, ProductDetailView, ProductVersionCreateView

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='list'),
    path('add/', ProductCreateView.as_view(), name='add'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='detail'),
    path('products/<slug:product_slug>/add-version/', ProductVersionCreateView.as_view(), name='add_version'),
]
