from django.contrib import admin

from .models import (
    Category,
    Message,
    Order,
    Payment,
    Repository,
    RepositoryCategory,
    Review,
    User,
)

admin.site.register(User)
admin.site.register(Repository)
admin.site.register(Category)
admin.site.register(RepositoryCategory)
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Review)
admin.site.register(Message)
