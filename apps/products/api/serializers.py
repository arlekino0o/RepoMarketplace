from rest_framework import serializers
from apps.orders.models import Order
from apps.products.models import Category, Product, ProductVersion, ProductReview
from apps.orders.models import OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent']


class ProductVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVersion
        fields = ['id', 'version_number', 'source_archive', 'changelog', 'created_at']
        read_only_fields = ['created_at']


# ==========================================================
# ОДИН ЕДИНСТВЕННЫЙ СЕРИАЛИЗАТОР ДЛЯ ОТЗЫВОВ (CRUD)
# ==========================================================
class ProductReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'username', 'rating', 'comment', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, attrs):
        # Эта валидация сработает только при отправке POST запроса
        request = self.context.get('request')
        if request and request.method == 'POST':
            user = request.user
            product_id = self.context['view'].kwargs.get('product_id')

            if ProductReview.objects.filter(product_id=product_id, user=user).exists():
                raise serializers.ValidationError("Вы уже оставили отзыв на этот продукт.")

            # Строгая проверка факта покупки оплаченного заказа
            has_purchased = Order.objects.filter(
                buyer=user,
                status__in=['paid', 'completed'],
                items__product_id=product_id
            ).exists()

            if not has_purchased:
                raise serializers.ValidationError("Вы не можете оставить отзыв на код, который не покупали.")
        return attrs


class ProductReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    seller = serializers.StringRelatedField(read_only=True)
    versions = ProductVersionSerializer(many=True, read_only=True)
    latest_version = serializers.SerializerMethodField()
    in_cart = serializers.SerializerMethodField()

    average_rating = serializers.FloatField(source='get_average_rating', read_only=True)
    reviews_count = serializers.IntegerField(source='get_reviews_count', read_only=True)
    has_purchased = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'short_description', 'description',
            'preview_image', 'demo_url', 'doc_url', 'price',
            'license_type', 'tech_stack', 'category', 'seller',
            'download_count', 'is_active', 'created_at', 'updated_at',
            'versions', 'latest_version', 'in_cart',
            'average_rating', 'reviews_count', 'has_purchased'
        ]

    def get_in_cart(self, obj):
        request = self.context.get('request')
        if not request:
            return False

        if request.user and request.user.is_authenticated:
            cart = Order.objects.filter(buyer=request.user, status='cart').first()

        return cart.items.filter(product=obj).exists() if cart else False

    def get_has_purchased(self, obj):
        request = self.context.get('request')
        if not request or not getattr(request, 'user', None) or not request.user.is_authenticated:
            return False

        return OrderItem.objects.filter(
            order__buyer=request.user,
            order__status__in=['paid', 'completed'],
            product_id=obj.id
        ).exists()

    def get_latest_version(self, obj):
        latest = obj.versions.first()
        return latest.version_number if latest else None

class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'title', 'slug', 'short_description', 'description',
            'preview_image', 'demo_url', 'doc_url', 'price',
            'license_type', 'tech_stack', 'category', 'is_active'
        ]

    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)

class ProductReviewReadSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'username', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'username', 'rating', 'comment', 'created_at']


class ProductReviewWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']

    def validate(self, attrs):
        user = self.context['request'].user
        product_id = self.context['view'].kwargs.get('product_id')

        if ProductReview.objects.filter(product_id=product_id, user=user).exists():
            raise serializers.ValidationError("Вы уже оставили отзыв на этот программный продукт.")

        has_purchased = Order.objects.filter(
            buyer=user,
            status__in=['paid', 'completed'],
            items__product_id=product_id
        ).exists()

        if not has_purchased:
            raise serializers.ValidationError("Вы не можете оценивать код, который вы не покупали.")

        return attrs


class ProductVersionUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVersion
        fields = ['version_number', 'source_archive', 'changelog']