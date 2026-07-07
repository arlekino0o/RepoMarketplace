from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
]