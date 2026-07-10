from rest_framework import serializers

from apps.orders.models import OrderItem
from apps.products.models import Repository
from apps.orders.models import Order


class RepositoryShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = ['id', 'title', 'price']


class OrderItemSerializer(serializers.ModelSerializer):
    repository = RepositoryShortSerializer(read_only=True)
    item_cost = serializers.ReadOnlyField(source='get_cost')

    class Meta:
        model = OrderItem
        fields = ['repository', 'quantity', 'item_cost']


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    status = serializers.CharField(read_only=True)

    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField(source='get_total_price')

    payment_id = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'buyer_id', 'seller_id', 'status', 'items', 'total_price', 'created_at', 'payment_id', 'email']
