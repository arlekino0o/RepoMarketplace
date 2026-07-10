from django.urls import path
from apps.users.api.views import RegisterView

app_name = 'users-api'

urlpatterns = [path('register/', RegisterView.as_view(), name='register'),]