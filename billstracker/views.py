from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import Http404
from django import forms
from datetime import datetime
from django.db import transaction
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth import login

from dateutil.relativedelta import relativedelta

from .models import BillDetail, Bill, Payment, PaymentStatus, BillCategory


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
    context = super().get_context_data(**kwargs)
    context['bills'] = context['bills'].filter(user=self.request.user)
    
    search_input = self.request.GET.get('search_area') or ''
    if search_input:
      context['bills'] = context['bills'].filter(bill_detail__name__icontains=search_input)
    
    return context
 

class CreateBill(LoginRequiredMixin, CreateView):
  model = Bill
  context_object_name = 'bills'
  template_name = 'create_bill.html'
  fields = ['due_date',
            'amount']
  success_url = reverse_lazy('bills-tracker')
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      
      context['category'] = BillCategory.objects.all()
      context['is_recurring_choices'] = BillDetail._meta.get_field('is_recurring').choices
      
      return context
  
  def form_valid(self, form):
    recurring_value = self.request.POST.get('is_recurring')
    recurring_count = int(self.request.POST.get('recurring_days'))
    
    form_due_date = form.cleaned_data['due_date']
    
    with transaction.atomic():
      category_instance = BillCategory.objects.get(id=self.request.POST.get('category'))
      
      bill_details = BillDetail(
            name = self.request.POST.get('name'),
            category = category_instance,
            description = self.request.POST.get('description'),
            is_recurring = self.request.POST.get('is_recurring')
        )
      
      bill_details.save()
      
      form.instance.user = self.request.user
      form.instance.bill_detail = bill_details
      form.instance.amount_payable = form.cleaned_data['amount']
      
      # bill = Bill(
      #         user = self.request.user,
      #         bill_detail = bill_details,
      #         amount = form_amount,
      #         amount_payable = form_amount,
      #         due_date = form_due_date
      #       )
      
      # bill.save()
      
      if not recurring_value == 'one-time':
        for i in range(1, recurring_count):
          if recurring_value == 'daily':
            form_due_date += relativedelta(days=1)
          elif recurring_value == 'monthly':
            form_due_date += relativedelta(months=1)
          elif recurring_value == 'yearly':
            form_due_date += relativedelta(years=1)
              
          bill = Bill(
            user = self.request.user,
            bill_detail = bill_details,
            amount = form.cleaned_data['amount'],
            amount_payable = form.cleaned_data['amount'],
            due_date = form_due_date
          )
            
          bill.save()
          
    return super().form_valid(form)
   

class BillDetailView(LoginRequiredMixin, DetailView):
  model = Bill
  template_name = 'bill_detail.html'
  context_object_name = 'bills'
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['payment'] = Payment.objects.filter(bill=self.kwargs['pk'])
    context['details'] = get_object_or_404(BillDetail, id=self.kwargs['d_id'])
    context['bill_total_amount'] = Bill.objects.filter(bill_detail = self.kwargs['d_id']).aggregate(total=Sum('amount'))['total']
    
    payment_total = Payment.objects.filter(bill = self.kwargs['pk']).aggregate(total=Sum('amount'))['total'] or 0
    
    context['bill_total_amount_payable'] = context['bill_total_amount'] - payment_total
    
    return context
  
  
  def get_object(self, queryset = None):
    obj = super().get_object(queryset=queryset)
    if obj.user != self.request.user:
      raise Http404("Product does not exist or you do not have permission to view it.")
    
    return obj
  
  
class BillView(LoginRequiredMixin, DetailView):
  model = Bill
  template_name = 'bill.html'
  context_object_name = 'bills'
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['details'] = get_object_or_404(BillDetail, id=self.object.bill_detail.id)
      context['payments'] = Payment.objects.filter(bill=self.kwargs['pk'])
      
      class PaymentForm(forms.ModelForm):
        class Meta:
          model = Payment
          fields = ['payment_reference', 'payment_type', 'amount', 'fee_amount']
      
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
  

class UpdateBill(LoginRequiredMixin, UpdateView):
  model = BillDetail
  context_object_name = 'bill'
  template_name = 'edit_bill.html'
  fields = ['name',
            'category',
            'description',
            'due_date',
            'amount',
            'is_recurring']
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_success_url(self):
    return reverse_lazy('bill-view', kwargs={'pk': self.object.pk})
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    bill_id = self.kwargs['pk']
    payments = Payment.objects.filter(bill=bill_id)
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
  model = Payment
  context_object_name = 'payment'
  template_name = 'paybill.html'
  fields = ['payment_reference', 'payment_type', 'amount', 'fee_amount']
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    bill_id = self.kwargs['b_id']
    detail_id = self.kwargs['d_id']
    
    context['details'] = get_object_or_404(BillDetail, id=detail_id)
    context['bill'] = get_object_or_404(Bill, id=bill_id)
    
    return context
  
  def form_valid(self, form):
      with transaction.atomic():
        bill_id = self.kwargs['b_id']
        
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
        
        return redirect('bill-view', pk=bill_id)
      
      return response
  
  def get_success_url(self):
    return reverse_lazy('bills-tracker')