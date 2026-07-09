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
    def _check_permissions(self, request, order):
        if order.user and request.user.is_authenticated and request.user == order.user:
            return True

        if order.session_key and request.session.session_key == order.session_key:
            return True

        raise PermissionDenied

    def get(self, request):
        order_id = int(request.GET.get("order_id"))
        order = get_object_or_404(Order, id=order_id)

        self._check_permissions(request, order)

        payment_provider = get_payment_provider()
        payment = payment_provider.create_payment(order_id, order.get_total_price())
        order.payment_id = payment["payment_id"]

        order.save()

        context = {
            'payment_id': payment['payment_id'],
            'order': order,
        }
        return render(request, "orders/mock_bank.html", context)

    def post(self, request):
        action = request.POST.get("action")
        order_id = request.POST.get("order_id")

        order = get_object_or_404(Order, id=order_id)
        self._check_permissions(request, order)

        if action == "success":
            order.status = "paid"
            order.save()
            return redirect("orders:success")
        else:
            order.status = "pending"
            order.save()
            return redirect("orders:failed")

class PaymentSuccessView(View):
    def get(self, request):
        return render(request, "orders/success.html")


class PaymentFailedView(View):
    def get(self, request):
        return render(request, "orders/failed.html")