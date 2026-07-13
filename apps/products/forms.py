from django import forms
from django.core.exceptions import ValidationError

from apps.products.models import Product, ProductVersion, Category


class ProductCreateForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Telegram Bot на Django'})
    )
    slug = forms.SlugField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'telegram-bot-django'})
    )
    short_description = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Краткое описание для карточки в каталоге'})
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Вставьте сюда README или подробное описание'})
    )
    preview_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    demo_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://mysite.com'})
    )
    doc_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://mysite.com'})
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    license_type = forms.ChoiceField(
        choices=Product.LICENSE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tech_stack = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Python, Django, PostgreSQL'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    version_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: 1.0.0'})
    )
    source_archive = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    changelog = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Что нового в этой версии?'})
    )

    def save(self, seller):
        cleaned_data = self.cleaned_data

        product = Product.objects.create(
            seller=seller,
            title=cleaned_data['title'],
            slug=cleaned_data['slug'],
            short_description=cleaned_data['short_description'],
            description=cleaned_data['description'],
            preview_image=cleaned_data['preview_image'],
            demo_url=cleaned_data['demo_url'],
            doc_url=cleaned_data['doc_url'],
            price=cleaned_data['price'],
            license_type=cleaned_data['license_type'],
            tech_stack=cleaned_data['tech_stack'],
            category=cleaned_data['category'],
            is_active=cleaned_data['is_active']
        )

        ProductVersion.objects.create(
            product=product,
            version_number=cleaned_data['version_number'],
            source_archive=cleaned_data['source_archive'],
            changelog=cleaned_data['changelog']
        )

        return product

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')

        if Product.objects.filter(slug=slug).exists():
            raise ValidationError("Товар с таким URL-адресом (слагом) уже существует. Придумайте другой.")

        return slug


class ProductVersionForm(forms.ModelForm):
    class Meta:
        model = ProductVersion
        fields = ['version_number', 'source_archive', 'changelog']
        widgets = {
            'version_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: 1.1.0'}),
            'source_archive': forms.FileInput(attrs={'class': 'form-control'}),
            'changelog': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Что изменилось в этой версии?'}),
        }