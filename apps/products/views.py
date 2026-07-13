from django.contrib.auth import forms
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction
from rest_framework.exceptions import PermissionDenied
from rest_framework.reverse import reverse

from apps.products.models import Product, ProductVersion
from .forms import ProductCreateForm, ProductVersionForm


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category', 'seller')


class ProductCreateView(LoginRequiredMixin, FormView):
    form_class = ProductCreateForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:list')
    login_url = reverse_lazy('users:login')

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save(seller=self.request.user)

        return super().form_valid(form)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category', 'seller')


class ProductVersionCreateView(LoginRequiredMixin, CreateView):
    model = ProductVersion
    form_class = ProductVersionForm
    template_name = 'products/add_version.html'
    login_url = reverse_lazy('users:login')

    # Переопределяем метод, чтобы проверить права и привязать версию к продукту
    def form_valid(self, form):
        # 1. Находим продукт по слагу из URL
        product = get_object_or_404(Product, slug=self.kwargs.get('product_slug'))

        # 2. Безопасность: проверяем, что текущий юзер — это продавец товара
        if product.seller != self.request.user:
            raise PermissionDenied("Вы не можете добавлять версии к чужому товару.")

        # 3. Привязываем продукт к форме версии
        form.instance.product = product
        return super().form_valid(form)

    # После успешной загрузки возвращаем разработчика на страницу самого товара
    def get_success_url(self):
        return reverse('products:detail', kwargs={'slug': self.kwargs.get('product_slug')})
