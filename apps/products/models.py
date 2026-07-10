from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.conf import settings

class Category(MPTTModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Слаг (URL)")
    
    parent = TreeForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children', 
        db_index=True,
        verbose_name="Родительская категория"
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название товара")
    description = models.TextField(verbose_name="Описание", null=True, blank=True)
    image = models.ImageField(upload_to='items/', blank=True, null=True, verbose_name="Foto товара")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    stock = models.PositiveIntegerField(default=0, verbose_name="Наличие (количество)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    category = TreeForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='items', 
        verbose_name="Категория",
        
        null=True,   
        blank=True
        
    )
    
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='products',
        verbose_name="Продавец",
        
        null=True,  
        blank=True
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def __str__(self):
        return self.title