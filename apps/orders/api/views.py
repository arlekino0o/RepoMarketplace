from django.urls import reverse
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction

from apps.orders.models import Order, OrderItem
from apps.products.models import Product
from apps.orders.api.serializers import OrderSerializer
from apps.orders.services.payment import get_payment_provider


class CartViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def _get_current_cart(self, request):
        cart, _ = Order.objects.get_or_create(buyer=request.user, status='cart')
        return cart

    def list(self, request, *args, **kwargs):
        cart = self._get_current_cart(request)
        serializer = OrderSerializer(cart)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({"error": "product_id обязателен."}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)
        cart = self._get_current_cart(request)

        # Избавились от количества: товар либо создается, либо игнорируется, если уже в корзине
        OrderItem.objects.get_or_create(order=cart, product=product)

        return Response(OrderSerializer(cart).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        cart = self._get_current_cart(request)
        # Удаляем товар из корзины по id продукта (pk)
        order_item = get_object_or_404(OrderItem, order=cart, product_id=pk)
        order_item.delete()

        return Response(OrderSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = self._get_current_cart(request)
        cart.items.all().delete()
        return Response(OrderSerializer(cart).data)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.exclude(status='cart').filter(buyer=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        orders = self.get_queryset()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        items_data = request.data.get('items', [])

        if not items_data:
            return Response(
                {"detail": "Не выбрано ни одного товара для оформления заказа."},
                status=status.HTTP_400_BAD_REQUEST
            )

        selected_item_ids = [item.get('id') for item in items_data]
        user = request.user

        cart_order = Order.objects.filter(buyer=user, status='cart').first()

        if not cart_order:
            return Response(
                {"detail": "Ваша корзина пуста или не найдена."},
                status=status.HTTP_400_BAD_REQUEST
            )

        all_cart_items = cart_order.items.all()
        selected_cart_items = all_cart_items.filter(id__in=selected_item_ids)

        if not selected_cart_items.exists():
            return Response(
                {"detail": "Выбранные товары не найдены в вашей корзине."},
                status=status.HTTP_400_BAD_REQUEST
            )

        is_full_checkout = all_cart_items.count() == selected_cart_items.count()

        if is_full_checkout:
            final_order = cart_order
            final_order.status = 'pending'
            final_order.save()

            for item in selected_cart_items:
                item.price_at_purchase = item.product.price
                item.save()
        else:
            final_order = Order.objects.create(
                buyer=user,
                email=user.email if hasattr(user, 'email') else None,
                status='pending',
                seller=selected_cart_items.first().product.seller if hasattr(selected_cart_items.first().product, 'seller') else None
            )

            for item in selected_cart_items:
                item.order = final_order
                item.price_at_purchase = item.product.price
                item.save()

        payment_url = f"/orders/mock-payment-page/?order_id={final_order.id}"

        return Response({
            "order_id": final_order.id,
            "payment_url": payment_url,
            "detail": "Заказ успешно переведен в статус ожидания оплаты."
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def initiate_payment(self, request, pk=None):
        order = get_object_or_404(Order, id=pk)

        if order.buyer_id != request.user.id:
            return Response({"detail": "Доступ запрещен: вы не владелец заказа."}, status=status.HTTP_403_FORBIDDEN)

        if order.status != 'pending':
            return Response({"detail": "Заказ уже оплачен или завершен."}, status=status.HTTP_400_BAD_REQUEST)

        payment_provider = get_payment_provider()
        payment = payment_provider.create_payment(order.id, order.get_total_price())
        order.payment_id = payment["payment_id"]
        order.save()

        return Response({
            "order_id": order.id,
            "total_price": float(order.get_total_price()),
            "payment_id": payment["payment_id"]
        })

    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        order = get_object_or_404(Order, id=pk)

        if order.buyer_id != request.user.id:
            return Response({"detail": "Доступ запрещен."}, status=status.HTTP_403_FORBIDDEN)

        action_type = request.data.get("action")

        if action_type == "success":
            order.status = "paid"
            order.save()
            return Response({"status": "paid", "redirect_to": reverse("orders:success")})
        else:
            order.status = "pending"
            order.save()
            return Response({"status": "pending", "redirect_to": reverse("orders:failed")})
