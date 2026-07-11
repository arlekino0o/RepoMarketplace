from django.urls import path

from . import message_views, views

app_name = 'marketplace'

urlpatterns = [
    path('repositories/', views.RepositoryListView.as_view(), name='repository_list'),
    path('repositories/create/', views.RepositoryCreateView.as_view(), name='repository_create'),
    path('repositories/<int:pk>/', views.RepositoryDetailView.as_view(), name='repository_detail'),
    path('repositories/<int:pk>/edit/', views.RepositoryUpdateView.as_view(), name='repository_update'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/<slug:slug>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<slug:slug>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('repositories/<int:repository_id>/buy/', views.OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/pay/', views.PaymentCreateView.as_view(), name='payment_create'),
    path('repositories/<int:repository_id>/reviews/', views.ReviewListView.as_view(), name='review_list'),
    path('orders/<int:order_id>/review/', views.ReviewCreateView.as_view(), name='review_create'),
    path('messages/', message_views.DialogListView.as_view(), name='message_list'),
    path('messages/<int:user_id>/', message_views.ConversationView.as_view(), name='message_conversation'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('users/<int:pk>/', views.UserProfileView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', views.UserProfileUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/repositories/', views.UserRepositoryListView.as_view(), name='user_repository_list'),
]
