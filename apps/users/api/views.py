from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from apps.users.api.serializers import RegisterSerializer


class RegisterView(CreateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer