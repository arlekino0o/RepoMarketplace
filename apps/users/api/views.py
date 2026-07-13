from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.api.serializers import RegisterSerializer, CurrentUserSerializer


class RegisterView(CreateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated] # Доступ только по токену

    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)