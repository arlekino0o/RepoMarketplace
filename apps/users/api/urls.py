from django.urls import path
from apps.users.api.views import RegisterView, CurrentUserAPIView

app_name = 'users-api'

urlpatterns = [path('register/', RegisterView.as_view(), name='register'),
               path('me/', CurrentUserAPIView.as_view(), name='current_user'),]