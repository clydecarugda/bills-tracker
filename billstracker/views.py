from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import Http404, HttpResponseRedirect
from django import forms
from datetime import datetime
from django.db import transaction
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth import login, authenticate, update_session_auth_hash
import django.contrib.auth.password_validation as password_validation

from dateutil.relativedelta import relativedelta

from .models import BillDetail, Bill, Payment, PaymentStatus, BillCategory, User, AuditLog, AccountGroup, MoneyAccount


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
      context['userprofile'] = self.request.user.userprofile

      return context
    
  def get_object(self, queryset = None):
    obj = super().get_object(queryset=queryset)
    
    if obj.id != self.request.user.id:
      raise Http404("Product does not exist or you do not have permission to view it.")
    
    return obj
  
  def form_valid(self, form):
      form.instance.id = self.request.user.id
      response = super().form_valid(form)
      
      profile = self.request.user.userprofile
      if self.request.FILES.get('prof_picture'):
        profile.profile_picture = self.request.FILES['prof_picture']
        
      if self.request.POST.get('dark_mode') == 'on':
        profile.dark_mode = True
      else:
        profile.dark_mode = False
        
      profile.save()
      
      return response
  

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
    

class AccountView(LoginRequiredMixin, ListView):
  model = MoneyAccount
  context_object_name = 'money_account'
  template_name = 'money_dashboard.html'
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      
      context['money_account'] = self.model.objects.filter(user=self.request.user)
      context['account_group'] = AccountGroup.objects.filter(user=self.request.user)

      return context
  
  def get_object(self, queryset = None):
    obj = super().get_object(queryset=queryset)
    
    if obj.user.id != self.request.user.id:
      raise Http404("The item you attempted to view does not exist or you don't have permission to view it.")
    
    return obj
  
class MoneyAccountList(LoginRequiredMixin, ListView):
  model = MoneyAccount
  context_object_name = 'money_account'
  template_name = 'money_accounts.html'
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      
      account_groups = AccountGroup.objects.filter(user=self.request.user)
      money_accounts = self.model.objects.filter(user=self.request.user)
      
      account_group_total = account_groups.model.objects.annotate(total_amount=Sum('moneyaccount__amount'))
      
      for group in account_group_total:
        group.accounts = money_accounts.model.objects.filter(account_group=group)
      
      context['money_account_list'] = money_accounts
      context['account_groups'] = account_group_total

      return context
  
class MoneyAccountAdd(LoginRequiredMixin, CreateView):
  model = MoneyAccount
  context_object_name = 'money_account'
  fields = ['account_group',
            'name',
            'amount',
            'description']
  template_name = 'money_account_add.html'
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  success_url = reverse_lazy('money-accounts')
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)

      return context
  
  def form_valid(self, form):
    form.instance.user = self.request.user
    
    with transaction.atomic():
      form_amount = self.request.POST.get('amount')
      
      response = super().form_valid(form)
      account_id = self.object
      
      TransactionHistoryLogger.log_transaction(
        user_id = self.request.user,
        bill_id = None,
        payment_reference = None,
        account_id = account_id,
        transaction_type = 'New Money Account',
        amount = form_amount,
        fee_amount = 0,
        note = None,
        payment_date_time = datetime.now()
      )
      
    return response
    
    
class MoneyAccountView(LoginRequiredMixin, DetailView):
  model = MoneyAccount
  context_object_name = 'money_account'
  template_name = 'money_account_view.html'
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_object(self, queryset = None):
    obj = super().get_object(queryset=queryset)
    
    if obj.user.id != self.request.user.id:
      raise Http404("The item you attempted to view does not exist or you don't have permission to view it.")
    
    return obj
  
class MoneyAccountDelete(LoginRequiredMixin, DeleteView):
  model = MoneyAccount
  context_object_name = 'money_account'
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  success_url = reverse_lazy('money-accounts')
  
  def get_object(self, queryset = None):
    obj = super().get_object(queryset=queryset)
    if obj.user != self.request.user:
      raise Http404("Product does not exist or you do not have permission to view it.")
    
    return obj
  

class MoneyAccountUpdate(LoginRequiredMixin, UpdateView):
  model = MoneyAccount
  context_object_name = 'money_account'
  template_name = 'money_account_edit.html'
  fields = ['name',
            'account_group',
            'amount',
            'description']
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_object(self, queryset = None):
    obj = super().get_object(queryset)
    
    if obj.user != self.request.user:
      raise Http404("The item you attempted to view does not exist or you don't have permission to view it.")
    
    return obj
  
  def form_valid(self, form):
    form.instance.user = self.request.user
    
    response = super().form_valid(form)
    
    return redirect('money-accounts-view', pk=self.kwargs['pk'])


class MoneyTransfer(LoginRequiredMixin, CreateView):
  model = Payment
  context_object_name = 'payment'
  fields = ['amount',
            'fee_amount',
            'note',
            'payment_date_time']
  template_name = 'money_transfer.html'
  login_url = ' login'
  redirect_field_name = 'redirect_to'
  success_url = reverse_lazy('money-accounts')
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['datetime_now'] = datetime.now().strftime('%Y-%m-%dT%H:%M')
      context['money_account_list'] = MoneyAccount.objects.filter(user=self.request.user)

      return context

  def form_valid(self, form):
      sender_id = self.request.POST.get('sender_account')
      receiver_id = self.request.POST.get('receiver_account')
      amount = float(form.cleaned_data.get('amount'))
      fee_amount = float(form.cleaned_data.get('fee_amount'))
      payment_datetime = form.cleaned_data.get('payment_date_time')
      note = form.cleaned_data.get('note')
      
      sender_account = get_object_or_404(MoneyAccount, id=sender_id, user=self.request.user)
      receiver_account = get_object_or_404(MoneyAccount, id=receiver_id, user=self.request.user)
      
      if sender_id == receiver_id:
        form.add_error(None, 'You cannot transfer to the same account!')
        
        return self.form_invalid(form)
      
      else:
        with transaction.atomic():
          sender_account.amount -= amount + fee_amount
          sender_account.save()
          
          receiver_account.amount += amount
          receiver_account.save()
          
          # Create transaction history - sender
          sender_payment = Payment(
            user = self.request.user,
            account = sender_account,
            transaction_type = 'Money Transfer',
            amount = -abs(amount),
            fee_amount = -abs(fee_amount),
            note = note,
            payment_date_time = payment_datetime
          )
          
          sender_payment.save()
          
          # Create transaction history - receiver
          receiver_payment = Payment(
            user = self.request.user,
            account = receiver_account,
            transaction_type = 'Money Transfer',
            amount = amount,
            fee_amount = 0,
            note = note,
            payment_date_time = payment_datetime
          )
          
          receiver_payment.save()
      
      return super().form_valid(form)


class TransactionHistory(LoginRequiredMixin, ListView):
  model = Payment
  context_object_name = 'payments'
  template_name = 'money_transaction_history.html'
  login_url = 'login'
  redirect_field_name = 'redirect_to'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['payments'] = self.model.objects.filter(user=self.request.user)
    
    return context
  

class AccountGroupList(LoginRequiredMixin, ListView):
  model = AccountGroup
  context_object_name = 'account_groups'
  template_name = 'money_account_groups.html'
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['account_groups'] = self.model.objects.filter(user=self.request.user)
      
      return context
    

class AccountGroupAdd(LoginRequiredMixin, CreateView):
  model = AccountGroup
  context_object_name = 'account_groups'
  template_name = 'money_account_group_add.html'
  fields = ['name']
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  success_url = reverse_lazy('money-account-groups')
  
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      
      return context
    
  def form_valid(self, form):
      form_name = form.cleaned_data.get('name')
      
      check_name = self.model.objects.filter(user=self.request.user, name=form_name).exists()
      
      if check_name:
        form.add_error('name', 'The account group already exists!')
        
        return self.form_invalid(form)
      else:
        form.instance.user = self.request.user
      
      return super().form_valid(form)
    

class AccountGroupView(LoginRequiredMixin, DetailView):
  model = AccountGroup
  context_object_name = 'account_groups'
  template_name = 'money_account_group_view.html'
  login_url = 'login'
  
  def get_object(self, queryset = None):
    obj = super().get_object(queryset=queryset)
    if obj.user != self.request.user:
      raise Http404("Product does not exist or you do not have permission to view it.")
    
    return obj
  

class AccountGroupEdit(LoginRequiredMixin, UpdateView):
  model = AccountGroup
  context_object_name = 'account_groups'
  template_name = 'money_account_group_edit.html'
  fields = ['name']
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  
  def get_object(self, queryset = None):
    obj = super().get_object(queryset=queryset)
    if obj.user != self.request.user:
      raise Http404("Product does not exist or you do not have permission to view it.")
    
    return obj
  
  def form_valid(self, form):
      form_name = form.cleaned_data.get('name')
      
      check_name = self.model.objects.filter(user=self.request.user, name=form_name).exists()
      
      if check_name:
        form.add_error('name', 'The account group already exists!')
        
        return self.form_invalid(form)
      else:
        form.instance.user = self.request.user
      
      return super().form_valid(form)
    

class AccountGroupDelete(LoginRequiredMixin, DeleteView):
  model = AccountGroup
  context_object_name = 'account_groups'
  login_url = 'login'
  redirect_field_name = 'redirect_to'
  success_url = reverse_lazy('money-account-groups')
  
  def get_object(self, queryset = None):
    obj = super().get_object(queryset=queryset)
    if obj.user != self.request.user:
      raise Http404("Product does not exist or you do not have permission to view it.")
    
    return obj
  
      
class TransactionHistoryLogger:
  @staticmethod
  def log_transaction(user_id, bill_id, payment_reference, account_id, transaction_type, amount, fee_amount, note, payment_date_time):
    Payment.objects.create(
      user = user_id,
      bill = bill_id,
      payment_reference = payment_reference,
      account = account_id,
      transaction_type = transaction_type,
      amount = amount,
      fee_amount = fee_amount,
      note = note,
      payment_date_time = payment_date_time
    )
    

class AuditLogger:
  @staticmethod
  def log_audit(user, action_type, model_affected, record_id, old_value, new_value, ip_address, user_agent, action_description, action_success, url, referer_url):
    AuditLog.objects.create(
      user = user,
      action_type = action_type,
      model_affected = model_affected,
      record_id = record_id,
      old_value = old_value,
      new_value = new_value,
      ip_address = ip_address,
      user_agent = user_agent,
      action_description = action_description,
      action_success = action_success,
      url = url,
      referer_url = referer_url
    )