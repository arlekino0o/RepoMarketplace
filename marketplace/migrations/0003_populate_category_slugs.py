from django.db import migrations, models
from django.utils.text import slugify


def populate_category_slugs(apps, schema_editor):
    Category = apps.get_model('marketplace', 'Category')
    for category in Category.objects.filter(slug__isnull=True):
        base_slug = slugify(category.name) or f'category-{category.pk}'
        slug = base_slug
        suffix = 2
        while Category.objects.filter(slug=slug).exclude(pk=category.pk).exists():
            slug = f'{base_slug}-{suffix}'
            suffix += 1
        category.slug = slug
        category.save(update_fields=['slug'])


class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0002_alter_user_managers_remove_user_password_hash_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_category_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(max_length=100, unique=True),
        ),
    ]
