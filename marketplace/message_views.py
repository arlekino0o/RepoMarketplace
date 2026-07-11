from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, TemplateView

from .message_forms import MessageForm
from .models import Message, User


class DialogListView(LoginRequiredMixin, ListView):
    template_name = 'marketplace/message_list.html'
    context_object_name = 'dialogs'

    def get_queryset(self):
        messages = (
            Message.objects.filter(Q(sender=self.request.user) | Q(receiver=self.request.user))
            .select_related('sender', 'receiver')
            .order_by('-created_at')
        )

        dialogs = []
        seen_user_ids = set()
        for message in messages:
            other_user = message.receiver if message.sender_id == self.request.user.id else message.sender
            if other_user.id not in seen_user_ids:
                dialogs.append({'user': other_user, 'last_message': message})
                seen_user_ids.add(other_user.id)
        return dialogs


class ConversationView(LoginRequiredMixin, TemplateView):
    template_name = 'marketplace/message_conversation.html'

    def dispatch(self, request, *args, **kwargs):
        self.other_user = User.objects.filter(pk=kwargs['user_id']).first()
        if not self.other_user or self.other_user.pk == request.user.pk:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['other_user'] = self.other_user
        context['conversation'] = (
            Message.objects.filter(
                Q(sender=self.request.user, receiver=self.other_user)
                | Q(sender=self.other_user, receiver=self.request.user)
            )
            .select_related('sender', 'receiver', 'repository')
            .order_by('created_at')
        )
        context['form'] = MessageForm()
        return context

    def post(self, request, *args, **kwargs):
        self.other_user = User.objects.filter(pk=kwargs['user_id']).first()
        if not self.other_user or self.other_user.pk == request.user.pk:
            raise Http404

        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = self.other_user
            message.save()
            return redirect(self.get_success_url())

        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse('marketplace:message_conversation', kwargs={'user_id': self.other_user.pk})
