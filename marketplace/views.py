from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import RepositoryForm
from .models import Category, Repository


class RepositoryListView(ListView):
    model = Repository
    template_name = 'marketplace/repository_list.html'
    context_object_name = 'repositories'
    paginate_by = 12

    def get_queryset(self):
        queryset = Repository.objects.select_related('seller').order_by('-created_at')
        query = self.request.GET.get('q')
        language = self.request.GET.get('language')
        status = self.request.GET.get('status')
        category_id = self.request.GET.get('category')

        if query:
            queryset = queryset.filter(title__icontains=query)
        if language:
            queryset = queryset.filter(language__iexact=language)
        if status:
            queryset = queryset.filter(status=status)
        if category_id:
            queryset = queryset.filter(repository_categories__category_id=category_id)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['statuses'] = Repository.Status.choices
        return context


class RepositoryDetailView(DetailView):
    model = Repository
    template_name = 'marketplace/repository_detail.html'
    context_object_name = 'repository'

    def get_queryset(self):
        return Repository.objects.select_related('seller')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(repository_categories__repository=self.object)
        return context


class RepositoryCreateView(CreateView):
    model = Repository
    form_class = RepositoryForm
    template_name = 'marketplace/repository_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Repository created successfully.')
        return response

    def get_success_url(self):
        return reverse_lazy('marketplace:repository_detail', kwargs={'pk': self.object.pk})


class RepositoryUpdateView(UpdateView):
    model = Repository
    form_class = RepositoryForm
    template_name = 'marketplace/repository_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Repository updated successfully.')
        return response

    def get_success_url(self):
        return reverse_lazy('marketplace:repository_detail', kwargs={'pk': self.object.pk})
