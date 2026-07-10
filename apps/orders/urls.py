from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('mock-payment-page/', views.PaymentsView.as_view(), name='payment'),
    path('payment/success/', views.PaymentSuccessView.as_view(), name='success'),
    path('payment/failed/', views.PaymentFailedView.as_view(), name='failed'),

    path('', views.OrdersView.as_view(), name='orders'),
]