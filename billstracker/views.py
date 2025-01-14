from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import Http404

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
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


class BillList(LoginRequiredMixin, ListView):
  model = Bill
  template_name = 'bills.html'
  context_object_name = 'bills'
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_context_data(self, **kwargs):
    search_input = self.request.GET.get('search_area') or ''
    context = super().get_context_data(**kwargs)
    context['bills'] = context['bills'].filter(user_id=self.request.user)
    
    if search_input:
      context['bills'] = context['bills'].filter(name__contains = search_input)
      
      context['search_input'] = search_input
      
    else:
      context['bills'] = context['bills'].filter(user_id=self.request.user)
    
    
    return context
  

class BillDetail(LoginRequiredMixin, DetailView):
  model = Bill
  template_name = 'bill.html'
  context_object_name = 'bills'
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_object(self, queryset = None):
    obj = super().get_object(queryset=queryset)
    if obj.user_id != self.request.user:
      raise Http404("Product does not exist or you do not have permission to view it.")
    
    return obj
  

class DeleteBill(LoginRequiredMixin, DeleteView):
  model = Bill
  context_object_name = 'bills'
  success_url = reverse_lazy('bills-tracker')
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_object(self, queryset = None):
    obj = super().get_object(queryset=queryset)
    if obj.user_id != self.request.user:
      raise Http404("Product does not exist or you do not have permission to view it.")
    
    return obj