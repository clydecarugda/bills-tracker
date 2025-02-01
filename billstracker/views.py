from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import Http404
from django import forms
from datetime import datetime
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.core.exceptions import ObjectDoesNotExist

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth import login, authenticate, update_session_auth_hash
import django.contrib.auth.password_validation as password_validation

from dateutil.relativedelta import relativedelta

from .models import BillDetail, Bill, Payment, PaymentStatus, BillCategory, User


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
    bills = self.model.objects.filter(user=self.request.user)
    context['bills'] = bills.exclude(payment_status=PaymentStatus.objects.get(name='Paid'))
    context['date_month_now'] = datetime.now().month
    context['date_year_now'] = datetime.now().year
    
    # search_input = self.request.GET.get('search_area') or ''
    # context['selected_month'] = self.request.GET.get('selected_month', None)
    # if search_input:
    #   context['bills'] = context['bills'].filter(bill_detail__name__icontains=search_input)
    
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
    
    form_due_date_primary = form.cleaned_data['due_date']
    
    with transaction.atomic():
      category_instance = BillCategory.objects.get(id=self.request.POST.get('category'))
      
      bill_details = BillDetail(
            user = self.request.user,
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
            form_due_date = form_due_date_primary + relativedelta(days=i)
          elif recurring_value == 'monthly':
            form_due_date = form_due_date_primary + relativedelta(months=i)
          elif recurring_value == 'yearly':
            form_due_date = form_due_date_primary + relativedelta(years=i)
              
          bill = Bill(
            user = self.request.user,
            bill_detail = bill_details,
            amount = form.cleaned_data['amount'],
            amount_payable = form.cleaned_data['amount'],
            due_date = form_due_date
          )
            
          bill.save()
          
    return super().form_valid(form)
   

class CreateCategory(LoginRequiredMixin, CreateView):
  model = BillCategory
  template_name = 'new_category.html'
  context_object_name = 'category'
  fields = ['name']
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  success_url = reverse_lazy('create-bill')
      
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)

      return context
    
  def form_valid(self, form):

    return super().form_valid(form)
  
  

class BillDetailView(LoginRequiredMixin, DetailView):
  model = BillDetail
  template_name = 'bill_detail.html'
  context_object_name = 'bill_detail'
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    bill = Bill.objects.filter(bill_detail=self.kwargs['pk'])
    context['bills'] = bill
    
    context['bill_total_amount'] = Bill.objects.filter(bill_detail = self.kwargs['pk']).aggregate(total=Sum('amount'))['total']
    
    payment_total = Bill.objects.filter(bill_detail = self.kwargs['pk'], payment_status=PaymentStatus.objects.get(name='Paid')).aggregate(total=Sum('amount'))['total'] or 0
    
    context['fee_total'] = 0
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
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_success_url(self):
    current_url = self.request.META.get('HTTP_REFERER', '')
    if 'billdetail' in current_url:
      return current_url
    else:
      return reverse_lazy('bills-tracker')
  
  def get_object(self, queryset = None):
    obj = super().get_object(queryset=queryset)
    if obj.user != self.request.user:
      raise Http404("Product does not exist or you do not have permission to view it.")
    
    return obj
  

class DeleteBillDetail(LoginRequiredMixin, DeleteView):
  model = BillDetail
  login_url = 'url'
  redirect_field_name = 'redirect_to'
  
  def get_success_url(self):
    return reverse_lazy('bills-tracker')
  
  def get_object(self, queryset = None):
    obj = super().get_object(queryset=queryset)
    
    if obj.user != self.request.user:
      raise Http404("Product does not exist or you do not have permission to view it.")
    
    return obj
  

class UpdateBill(LoginRequiredMixin, UpdateView):
  model = Bill
  context_object_name = 'bill'
  template_name = 'edit_bill.html'
  fields = ['due_date',
            'amount']
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    bill = self.get_object()
    
    context['details'] = bill.bill_detail
    context['category'] = BillCategory.objects.all()
    
    return context
  
  def form_valid(self, form):
    with transaction.atomic():
      category_instance = BillCategory.objects.get(id=self.request.POST.get('category'))
      bill_form = form.instance
      bill_detail = self.object.bill_detail
      
      bill_detail.name = self.request.POST.get('name')
      bill_detail.category = category_instance
      bill_detail.description = self.request.POST.get('description')
      bill_detail.save()
      
      total_paid = sum(pay.amount for pay in bill_form.pays.all())
      
      bill_form.amount_payable = bill_form.amount - total_paid
      bill_form.save()
      
      return redirect('bill-view', pk=self.kwargs['pk'])
        
    return super().form_valid(form)
  

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
  

class ProfileView(LoginRequiredMixin, UpdateView):
  model = User
  context_object_name = 'user'
  template_name = 'profile.html'
  fields = ['username',
            'email',
            'first_name',
            'last_name']
  success_url = reverse_lazy('bills-tracker')
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)

      return context
    
  def get_object(self, queryset = None):
    obj = super().get_object(queryset=queryset)
    
    if obj.id != self.request.user.id:
      raise Http404("Product does not exist or you do not have permission to view it.")
    
    return obj
  
  def form_valid(self, form):
      form.instance.id = self.request.user.id
      
      return super().form_valid(form)
  

class PasswordChange(LoginRequiredMixin, UpdateView):
  model = User
  context_object_name = 'user'
  template_name = 'changepassword.html'
  fields = ['password']
  success_url = reverse_lazy('bills-tracker')
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      
      context['password_help_text'] = password_validation.password_validators_help_text_html

      return context
    
  def get_object(self, queryset = None):
    obj = super().get_object(queryset=queryset)
    
    if obj.id != self.request.user.id:
      raise Http404("Product does not exist or you do not have permission to view it.")
    
    return obj
  
  def form_valid(self, form):
      current_password = form.cleaned_data.get('password')
      new_password = self.request.POST.get('new_password')
      re_new_password = self.request.POST.get('re_new_password')
      
      check_password = self.request.user.check_password(current_password)
      
      if check_password:
        if new_password != re_new_password:
          form.add_error(None, 'Both Password field should match')
          
          return self.form_invalid(form)         
        
      else:
        form.add_error('password', 'Wrong Password!!')
        
        return self.form_invalid(form)
      
      try:
        password_validation.validate_password(new_password)
        
        user = form.save(commit=False)
        
        user.set_password(new_password)
        user.save()
        
        update_session_auth_hash(self.request, user)
      
      except forms.ValidationError as error:
        form.add_error(None, error)

        return self.form_invalid(form)
      
      return super().form_valid(form)