from django import forms

from .models import Repository


class RepositoryForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = ['seller', 'title', 'description', 'price', 'language', 'repo_url', 'status', 'categories']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    categories = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Category
        self.fields['categories'].queryset = Category.objects.all()
        if self.instance.pk:
            self.fields['categories'].initial = Category.objects.filter(
                repository_categories__repository=self.instance
            )

    def save(self, commit=True):
        repository = super().save(commit=commit)
        if commit:
            self._save_categories(repository)
        else:
            self._pending_categories = self.cleaned_data.get('categories')
        return repository

    def _save_categories(self, repository):
        from .models import RepositoryCategory
        categories = self.cleaned_data.get('categories')
        RepositoryCategory.objects.filter(repository=repository).exclude(category__in=categories).delete()
        existing = set(RepositoryCategory.objects.filter(repository=repository).values_list('category_id', flat=True))
        for category in categories:
            if category.pk not in existing:
                RepositoryCategory.objects.create(repository=repository, category=category)


from .models import User


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'rating']
