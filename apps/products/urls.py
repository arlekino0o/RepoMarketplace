from django.urls import path
from apps.products import views

app_name = 'products'

urlpatterns = [
    #для репозиториев
    path('', views.RepositoryListView.as_view(), name='repository_list'), # или product_list
    
    #для категорий по паттерну entity_action
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/<slug:slug>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<slug:slug>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

]