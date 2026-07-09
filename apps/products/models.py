from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Слаг (URL)")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name


class Repository(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название репозитория")
    description = models.TextField(verbose_name="Описание", null=True, blank=True)
    image = models.ImageField(upload_to='repositories/', blank=True, null=True, verbose_name="Фото репозитория")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    
    # Булево поле для лицензии: True — коммерческая, False — личная 
    is_commercial_license = models.BooleanField(default=False, verbose_name="Коммерческая лицензия")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    #Связь Many-to-Many через автоматическую таблицу
    categories = models.ManyToManyField(
        Category, 
        related_name='repositories', 
        verbose_name="Категории"
    )
    
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='repositories',
        verbose_name="Продавец",
        null=True,  
        blank=True
    )

    class Meta:
        verbose_name = "Репозиторий"
        verbose_name_plural = "Репозитории"
        ordering = ['-created_at']

    def __str__(self):
        return self.title