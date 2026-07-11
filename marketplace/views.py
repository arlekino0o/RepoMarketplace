from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CategoryForm, LoginForm, RegisterForm, RepositoryForm, ReviewForm, UserProfileForm
from .models import Category, Order, Payment, Repository, Review, User


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
        context['reviews'] = Review.objects.filter(order__repository=self.object).select_related('order__buyer')
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


class UserProfileView(DetailView):
    model = User
    template_name = 'marketplace/user_detail.html'
    context_object_name = 'profile_user'


class UserProfileUpdateView(UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'marketplace/user_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Profile updated successfully.')
        return response

    def get_success_url(self):
        return reverse_lazy('marketplace:user_detail', kwargs={'pk': self.object.pk})


class UserRepositoryListView(ListView):
    model = Repository
    template_name = 'marketplace/user_repository.html'
    context_object_name = 'repositories'
    paginate_by = 12

    def get_queryset(self):
        self.owner = get_object_or_404(User, pk=self.kwargs['pk'])
        return Repository.objects.filter(seller=self.owner).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
        return context


class RegisterView(View):
    template_name = 'marketplace/register.html'

    def get(self, request):
        return render(request, self.template_name, {'form': RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('marketplace:repository_list')
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    template_name = 'marketplace/login.html'

    def get(self, request):
        return render(request, self.template_name, {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('marketplace:repository_list')
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('marketplace:login')


class CategoryListView(ListView):
    model = Category
    template_name = 'marketplace/category_list.html'
    context_object_name = 'categories'


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'marketplace/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['repositories'] = Repository.objects.filter(
            repository_categories__category=self.object
        ).select_related('seller')
        return context


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class CategoryCreateView(StaffRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'marketplace/category_form.html'
    success_url = reverse_lazy('marketplace:category_list')


class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'marketplace/category_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('marketplace:category_list')


class CategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = Category
    template_name = 'marketplace/category_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('marketplace:category_list')


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'marketplace/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).select_related('repository', 'payment')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'marketplace/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).select_related('repository', 'payment')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_review'] = (
            self.object.status == Order.Status.PAID
            and not Review.objects.filter(order=self.object).exists()
        )
        return context


class OrderCreateView(LoginRequiredMixin, View):
    def post(self, request, repository_id):
        repository = get_object_or_404(Repository, pk=repository_id, status=Repository.Status.ACTIVE)
        if repository.seller_id == request.user.id:
            raise Http404

        order = Order.objects.create(
            buyer=request.user,
            repository=repository,
            price=repository.price,
            status=Order.Status.PENDING,
        )
        messages.success(request, 'Order created. You can now complete payment.')
        return redirect('marketplace:order_detail', pk=order.pk)


class PaymentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, buyer=request.user)
        payment, _ = Payment.objects.get_or_create(
            order=order,
            defaults={'amount': order.price, 'method': 'mock', 'status': Payment.Status.PENDING},
        )
        payment.status = Payment.Status.SUCCESS
        payment.paid_at = timezone.now()
        payment.save()
        order.status = Order.Status.PAID
        order.save(update_fields=['status'])
        messages.success(request, 'Payment completed successfully.')
        return redirect('marketplace:order_detail', pk=order.pk)


class ReviewListView(ListView):
    model = Review
    template_name = 'marketplace/review_list.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        self.repository = get_object_or_404(Repository, pk=self.kwargs['repository_id'])
        return Review.objects.filter(order__repository=self.repository).select_related('order__buyer')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['repository'] = self.repository
        return context


class ReviewCreateView(LoginRequiredMixin, CreateView):
    form_class = ReviewForm
    template_name = 'marketplace/review_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.order = get_object_or_404(
            Order,
            pk=kwargs['order_id'],
            buyer=request.user,
            status=Order.Status.PAID,
        )
        if Review.objects.filter(order=self.order).exists():
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.order = self.order
        messages.success(self.request, 'Review created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('marketplace:repository_detail', kwargs={'pk': self.order.repository_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        return context
