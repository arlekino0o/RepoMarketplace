from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username