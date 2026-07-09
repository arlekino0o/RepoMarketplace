from django.urls import path

from . import message_views

app_name = 'marketplace'

urlpatterns = [
    path('messages/', message_views.DialogListView.as_view(), name='message_list'),
    path('messages/<int:user_id>/', message_views.ConversationView.as_view(), name='message_conversation'),
]
