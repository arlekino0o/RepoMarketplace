from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from apps.products.models import Category, Repository
from apps.products.forms import CategoryForm

#Views для Репозиториев
class RepositoryListView(ListView):
    model = Repository
    template_name = 'products/product_list.html'  
    context_object_name = 'repositories'


# Views для Категорий 

class CategoryListView(ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'products/category_detail.html'
    context_object_name = 'category'
    slug_url_kwarg = 'slug' # Django будет искать категорию по slug из URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Благодаря related_name='repositories' вытаскиваем связанные репозитории
        context['repositories'] = self.object.repositories.all()
        return context


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    # После создания перенаправляем на список категорий
    success_url = reverse_lazy('products:category_list') 


class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('products:category_list')
    
class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'products/category_confirm_delete.html'
    success_url = reverse_lazy('products:category_list')