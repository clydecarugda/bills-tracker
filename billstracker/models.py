from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


def user_directory_path(instance, filename):
  return f"profile_pics/{instance.user.id}/{filename}"


# Money Tracker
class AccountGroup(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  name = models.CharField(max_length=30)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.name
  
  class Meta:
    ordering = ['name']
    
  def get_absolute_url(self):
    return reverse('money-account-group-view', kwargs={'pk': self.pk}) 
  
  
class Category(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  name = models.CharField(max_length=30)
  category_type = models.CharField(max_length=15)
  show_name = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  class Meta:
    verbose_name_plural = 'Categories'
  
  def __str__(self):
    return self.name
  

class MoneyAccount(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  account_group = models.ForeignKey(AccountGroup, on_delete=models.CASCADE)
  name = models.CharField(max_length=30)
  amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
  description = models.TextField(null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return self.name
  
  def get_absolute_url(self):
    return reverse('money-accounts-view', kwargs={'pk': self.pk}) 
  
  
class AuditLog(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  action_type = models.CharField(max_length=30)
  model_affected = models.CharField(max_length=100)
  record_id = models.UUIDField()
  old_value = models.TextField()
  new_value = models.TextField()
  ip_address = models.GenericIPAddressField(null=True, blank=True)
  user_agent = models.CharField(max_length=255)
  action_description = models.TextField()
  action_success = models.BooleanField()
  url = models.CharField(max_length=200)
  referer_url = models.CharField(max_length=200)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return self.action_type
  

# Bills
class PaymentStatus(models.Model):
  name = models.CharField(max_length=30)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return self.name
  
  class Meta:
    verbose_name_plural = 'Payment Status'
    

class BillCategory(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
  name = models.CharField(max_length=30)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return self.name
  
  class Meta:
    verbose_name_plural = 'Bill Categories'
    

class BillDetail(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  name = models.CharField(max_length=30)
  category = models.ForeignKey(Category, on_delete=models.CASCADE)
  description = models.TextField(null=True, blank=True)
  is_recurring = models.CharField(max_length=15,
                                  choices=[('one-time', 'One-Time'),
                                           ('daily', 'Daily'),
                                           ('monthly', 'Monthly'),
                                           ('yearly', 'Yearly')],
                                  default='one-time')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return self.name
  

class Bill(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  bill_detail = models.ForeignKey(BillDetail, on_delete=models.CASCADE, related_name='bill_details')
  due_date = models.DateField()
  amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
  amount_payable = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
  payment_status = models.ForeignKey(PaymentStatus, default=1, on_delete=models.CASCADE)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return self.bill_detail.name
  
  class Meta:
    ordering = ['due_date']
  

class Payment(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
  bill = models.ForeignKey(Bill, on_delete=models.SET_NULL, related_name='pays', null=True)
  account = models.ForeignKey(MoneyAccount, on_delete=models.SET_NULL, null=True)
  payment_reference = models.CharField(max_length=100, null=True, blank=True)
  transaction_type = models.CharField(max_length=25, null=True)
  category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
  amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
  fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
  note = models.TextField(null=True, blank=True)
  payment_date_time = models.DateTimeField(null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __int__(self):
    return self.id
  
  class Meta:
    ordering = ['-payment_date_time']
    
    
class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  profile_picture = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
  dark_mode = models.BooleanField(default=False)
  
  def __str__(self):
        return self.user.username
      

class Feedback(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  name = models.CharField(max_length=50)
  feedback_message = models.TextField()
  review_check = models.BooleanField(default=False)
  admin_feedback = models.TextField(default='')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return self.name