import django.views
from django.shortcuts import render
from rest_framework import viewsets

from apps.products.models import Product


class ProductListView(django.views.generic.ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'