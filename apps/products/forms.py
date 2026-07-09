from django import forms
from apps.products.models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: DevOps или Веб-разработка'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: devops'}),
        }