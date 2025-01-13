from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.list import ListView

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login

from .models import Bill


class LoginPage(LoginView):
  template_name = 'login.html'
  fields = '__all__'
  redirect_authenticated_user = True
  
  def get_success_url(self):
    return reverse_lazy('main')
  

def MainPage(request):
  return render(request, 'main_page.html')