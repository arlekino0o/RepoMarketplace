from django.db import models

from apps.products.models import Repository
from config import settings


class Order(models.Model):
    STATUS_CHOICES = [
        ('cart', 'Корзина'),
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('completed', 'Завершен'),
    ]

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='cart')
    repositories = models.ManyToManyField(Repository, through='OrderItem', related_name='orders')

    email = models.EmailField(null=True, blank=True)

    payment_id = models.CharField(null=True, blank=True)

    def get_total_price(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def get_cost(self):
        price = self.price_at_purchase if self.price_at_purchase else self.repository.price
        return price * self.quantity