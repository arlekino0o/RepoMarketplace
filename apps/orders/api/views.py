from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.products.models import Repository
from apps.orders.models import Order, OrderItem
from apps.orders.api.serializers import OrderSerializer


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [AllowAny]

    def _get_current_cart(self, request):
        if request.user.is_authenticated:
            cart, _ = Order.objects.get_or_create(buyer=request.user, status='cart')
        else:
            if not request.session.session_key:
                request.session.create()
            cart, _ = Order.objects.get_or_create(session_key=request.session.session_key, status='cart')
        return cart

    def list(self, request, *args, **kwargs):
        cart = self._get_current_cart(request)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({"error": "product_id обязателен."}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Repository, id=product_id)
        cart = self._get_current_cart(request)

        # Изменили аргумент product=product на repository=product
        order_item, created = OrderItem.objects.get_or_create(
            order=cart, repository=product, defaults={'quantity': quantity}
        )
        if not created:
            order_item.quantity += quantity
            order_item.save()

        return Response(self.get_serializer(cart).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        cart = self._get_current_cart(request)
        # Здесь и ниже pk — это id репозитория
        order_item = get_object_or_404(OrderItem, order=cart, product_id=pk)

        quantity = request.data.get('quantity')
        if quantity is None or int(quantity) <= 0:
            return Response({"error": "Укажите корректное количество > 0."}, status=status.HTTP_400_BAD_REQUEST)

        order_item.quantity = int(quantity)
        order_item.save()

        return Response(self.get_serializer(cart).data)

    def partial_update(self, request, pk=None, *args, **kwargs):
        return self.update(request, pk, *args, **kwargs)

    def destroy(self, request, pk=None, *args, **kwargs):
        cart = self._get_current_cart(request)
        order_item = get_object_or_404(OrderItem, order=cart, repository_id=pk)
        order_item.delete()

        return Response(self.get_serializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = self._get_current_cart(request)
        cart.repositories.all().delete()
        return Response(self.get_serializer(cart).data)

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        cart = self._get_current_cart(request)

        if not cart.repositories.exists():
            return Response({"error": "Нельзя оформить пустую корзину."}, status=status.HTTP_400_BAD_REQUEST)

        cart.status = 'pending'

        if not request.user.is_authenticated:
            cart.email = request.data.get('email')
            if not cart.email:
                return Response({"error": "Email обязателен для гостей."},
                                status=status.HTTP_400_BAD_REQUEST)

        cart.save()

        return Response({
            "message": "Заказ успешно сформирован и ожидает оплаты.",
            "order_id": cart.pk,
            "total_price": cart.get_total_price()
        })


class OrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Order.objects.exclude(status='cart').filter(buyer=self.request.user)
        else:
            return Order.objects.exclude(status='cart').filter(session_key=self.request.session.session_key)

    def list(self, request, *args, **kwargs):
        orders = self.get_queryset()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)