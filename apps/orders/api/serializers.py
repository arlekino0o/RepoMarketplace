from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.orders.models import OrderItem
from apps.products.models import Product
from apps.orders.models import Order


class ProductShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'slug']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductShortSerializer(read_only=True)
    item_cost = serializers.ReadOnlyField(source='get_cost')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'item_cost']


class OrderSerializer(serializers.ModelSerializer):
    buyer = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        default=serializers.CurrentUserDefault(),
    )
    status = serializers.CharField(read_only=True)

    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField(source='get_total_price')

    payment_id = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'buyer',
            'seller',
            'status',
            'created_at',
            'email',
            'payment_id',
            'total_price',
            'items'
        ]
        read_only_fields = ['created_at', 'session_key']