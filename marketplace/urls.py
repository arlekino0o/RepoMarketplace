from django.urls import path

from . import message_views, views

app_name = 'marketplace'

urlpatterns = [
    path('repositories/', views.RepositoryListView.as_view(), name='repository_list'),
    path('repositories/create/', views.RepositoryCreateView.as_view(), name='repository_create'),
    path('repositories/<int:pk>/', views.RepositoryDetailView.as_view(), name='repository_detail'),
    path('repositories/<int:pk>/edit/', views.RepositoryUpdateView.as_view(), name='repository_update'),
    path('messages/', message_views.DialogListView.as_view(), name='message_list'),
    path('messages/<int:user_id>/', message_views.ConversationView.as_view(), name='message_conversation'),
]
