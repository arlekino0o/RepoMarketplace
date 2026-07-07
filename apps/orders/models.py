from django.contrib.auth.models import User
from django.db import models

from apps.products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('cart', 'Корзина'),
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('completed', 'Завершен'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='cart')
    products = models.ManyToManyField(Product, through='OrderItem', related_name='orders')

    email = models.EmailField(null=True, blank=True)

    def get_total_price(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def get_cost(self):
        price = self.price_at_purchase if self.price_at_purchase else self.product.price
        return price * self.quantity