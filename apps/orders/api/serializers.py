from rest_framework import serializers

from apps.orders.models import OrderItem
from apps.products.models import Product
from apps.orders.models import Order


class ProductShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductShortSerializer(read_only=True)
    item_cost = serializers.ReadOnlyField(source='get_cost')

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'item_cost']


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    status = serializers.CharField(read_only=True)

    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField(source='get_total_price')

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'items', 'total_price', 'created_at']
