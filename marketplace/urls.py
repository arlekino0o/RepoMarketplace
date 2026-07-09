from django.urls import path

from . import views

app_name = 'marketplace'

urlpatterns = [
    path('repositories/', views.RepositoryListView.as_view(), name='repository_list'),
    path('repositories/create/', views.RepositoryCreateView.as_view(), name='repository_create'),
    path('repositories/<int:pk>/', views.RepositoryDetailView.as_view(), name='repository_detail'),
    path('repositories/<int:pk>/edit/', views.RepositoryUpdateView.as_view(), name='repository_update'),
]
