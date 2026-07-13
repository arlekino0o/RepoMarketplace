from django.core.validators import MinValueValidator, MaxValueValidator
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
    LICENSE_CHOICES = [
        ('mit', 'MIT License'),
        ('gpl', 'GPL v3'),
        ('apache', 'Apache 2.0'),
        ('commercial_regular', 'Коммерческая (Обычная)'),
        ('commercial_extended', 'Коммерческая (Расширенная)'),
    ]

    title = models.CharField(max_length=255, verbose_name="Название цифрового товара")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Слаг товара")
    description = models.TextField(verbose_name="Подробное описание / README")
    short_description = models.CharField(max_length=255, verbose_name="Краткое описание для карточки")

    preview_image = models.ImageField(upload_to='products/previews/', blank=True, null=True,
                                      verbose_name="Превью (Скриншот/GIF)")
    demo_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на Live Demo")
    doc_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на документацию")

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    license_type = models.CharField(max_length=30, choices=LICENSE_CHOICES, default='commercial_regular',
                                    verbose_name="Тип лицензии")

    tech_stack = models.CharField(max_length=255, verbose_name="Стек технологий (через запятую или как теги)")

    category = TreeForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products',
                              verbose_name="Категория")
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products',
                               verbose_name="Продавец")

    download_count = models.PositiveIntegerField(default=0, verbose_name="Количество скачиваний")
    is_active = models.BooleanField(default=True, verbose_name="Доступен для покупки")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления")

    class Meta:
        verbose_name = "Товар (Код)"
        verbose_name_plural = "Товары (Код)"
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    def get_average_rating(self):
        avg = self.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0.0

    def get_reviews_count(self):
        return self.reviews.count()


class ProductVersion(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='versions', verbose_name="Товар")
    version_number = models.CharField(max_length=20, verbose_name="Номер версии (например, 1.0.4)")

    source_archive = models.FileField(upload_to='products/sources/%Y/%m/', verbose_name="Архив с кодом (.zip/.tar.gz)")

    changelog = models.TextField(blank=True, null=True, verbose_name="Что нового в этой версии")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата релиза версии")

    class Meta:
        verbose_name = "Версия продукта"
        verbose_name_plural = "Версии продуктов"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.title} - v{self.version_number}"


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Товар")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Покупатель")

    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка кода"
    )

    comment = models.TextField(verbose_name="Текст отзыва (что понравилось/не понравилось)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отзыва")

    class Meta:
        verbose_name = "Отзыв о коде"
        verbose_name_plural = "Отзывы о коде"
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.product.title} ({self.rating}★)"


class SellerReview(models.Model):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_reviews',
        verbose_name="Продавец"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Покупатель")

    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка поддержки"
    )

    comment = models.TextField(verbose_name="Отзыв о качестве коммуникации и помощи", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отзыва")

    class Meta:
        verbose_name = "Отзыв о продавце"
        verbose_name_plural = "Отзывы о продавцах"
        unique_together = ('seller', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв от {self.user.username} о продавце {self.seller.username} ({self.rating}★)"