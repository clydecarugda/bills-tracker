from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import Http404
from datetime import datetime
from django.db import transaction

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth import login

from .models import Bill, PaymentMethod, PaymentStatus


class LoginPage(LoginView):
  template_name = 'login.html'
  fields = '__all__'
  redirect_authenticated_user = True
  
  def get_success_url(self):
    return reverse_lazy('main')
  

class MainPage(LoginRequiredMixin ,TemplateView):
  template_name = 'main_page.html'
  login_url = 'login'
  redirect_field_name = 'redirect_to'


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
    context['bills'] = context['bills'].filter(payment_status__name__in=['Pending', 'Overdue', 'Partially Paid'])
    
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
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['payment'] = PaymentMethod.objects.filter(bill=self.kwargs['pk'])
    
    return context
  
  
  def get_object(self, queryset = None):
    obj = super().get_object(queryset=queryset)
    if obj.user != self.request.user:
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
    if obj.user != self.request.user:
      raise Http404("Product does not exist or you do not have permission to view it.")
    
    return obj
  

class CreateBill(LoginRequiredMixin, CreateView):
  model = Bill
  context_object_name = 'bills'
  template_name = 'create_bill.html'
  fields = ['name',
            'bill_type',
            'description',
            'due_date',
            'amount',
            'payment_status']
  success_url = reverse_lazy('bills-tracker')
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def form_valid(self, form):
    form.instance.user = self.request.user
    form.instance.amount_payable = form.cleaned_data['amount']
    
    return super().form_valid(form)
  

class UpdateBill(LoginRequiredMixin, UpdateView):
  model = Bill
  context_object_name = 'bill'
  template_name = 'edit_bill.html'
  fields = ['name',
            'bill_type',
            'description',
            'due_date',
            'amount',
            'payment_status']
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_success_url(self):
    return reverse_lazy('bill-view', kwargs={'pk': self.object.pk})
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    bill_id = self.kwargs['pk']
    payments = PaymentMethod.objects.filter(bill=bill_id)
    context['payments'] = payments
    
    return context
  
  def form_valid(self, form):
    response = super().form_valid(form)
    
    bill_form = form.instance
    
    total_paid = sum(pay.amount for pay in bill_form.pays.all())
    
    bill_form.amount_payable = bill_form.amount - total_paid
    
    bill_form.save()
      
    return response
  

class PayBill(LoginRequiredMixin, CreateView):
  model = PaymentMethod
  context_object_name = 'paymentmethod'
  template_name = 'paybill.html'
  fields = ['method_name', 'amount', 'fee_amount']
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    bill_id = self.kwargs['pk']
    context['bill'] = Bill.objects.get(pk=bill_id)
    
    return context
  
  def form_valid(self, form):
      with transaction.atomic():
        bill_id = self.kwargs['pk']
        
        bill = Bill.objects.select_for_update().get(id=bill_id)
        
        payment = form.save(commit=False)
        payment.bill = bill
        payment.save()
        
        response = super().form_valid(form)
        
        total_paid = sum(pay.amount for pay in bill.pays.all())
        bill.amount_payable = bill.amount - total_paid
        
        if bill.amount_payable <= 0:
          bill.payment_status = PaymentStatus.objects.get(name='Paid')
        else:
          bill.payment_status = PaymentStatus.objects.get(name='Partially Paid')
        
        bill.save()
        
        return redirect('bills-tracker')
      
      return response
  
  def get_success_url(self):
    return reverse_lazy('bills-tracker')