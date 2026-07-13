from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from apps.orders.models import Order

from apps.orders.services.payment import get_payment_provider


class CartView(View):
    def get(self, request):
        return render(request, "orders/cart.html")


class OrdersView(View):
    def get(self, request):
        return render(request, "orders/orders.html")


class PaymentsView(View):
    def get(self, request):
        return render(request, "orders/mock_bank.html")

class PaymentSuccessView(View):
    def get(self, request):
        return render(request, "orders/success.html")


class PaymentFailedView(View):
    def get(self, request):
        return render(request, "orders/failed.html")