from django.db import models
from django.contrib.auth.models import User


def user_directory_path(instance, filename):
  return f"profile_pics/{instance.user.id}/{filename}"


class PaymentStatus(models.Model):
  name = models.CharField(max_length=30)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.name
  
  class Meta:
    verbose_name_plural = 'Payment Status'
    

class BillCategory(models.Model):
  name = models.CharField(max_length=30)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.name
  
  class Meta:
    verbose_name_plural = 'Bill Categories'
    

class BillDetail(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  name = models.CharField(max_length=30)
  category = models.ForeignKey(BillCategory, on_delete=models.CASCADE)
  description = models.TextField(null=True, blank=True)
  is_recurring = models.CharField(max_length=15,
                                  choices=[('one-time', 'One-Time'),
                                           ('daily', 'Daily'),
                                           ('monthly', 'Monthly'),
                                           ('yearly', 'Yearly')],
                                  default='one-time')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.name
  

class Bill(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  bill_detail = models.ForeignKey(BillDetail, on_delete=models.CASCADE, related_name='bill_details')
  due_date = models.DateField()
  amount = models.FloatField()
  amount_payable = models.FloatField()
  payment_status = models.ForeignKey(PaymentStatus, default=1, on_delete=models.CASCADE)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.bill_detail.name
  
  class Meta:
    ordering = ['payment_status', 'due_date']
    

class PaymentType(models.Model):
  name = models.CharField(max_length=25)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.name

class Payment(models.Model):
  bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='pays')
  payment_reference = models.CharField(max_length=100, null=True, blank=True)
  payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
  amount = models.FloatField()
  fee_amount = models.FloatField(default=0)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.bill.bill_detail.name
    
    
class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  profile_picture = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
  dark_mode = models.BooleanField(default=False)
  
  def __str__(self):
        return self.user.username