from django.shortcuts import render
from django.views import View


class LoginView(View):
    def get(self, request):
        return render(request, 'users/login.html')

class LogoutView(View):
    def get(self, request):
        return render(request, 'users/logout.html')

class RegisterView(View):
    def get(self, request):
        return render(request, 'users/register.html')

