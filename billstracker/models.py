from django.db import models
from django.contrib.auth.models import User


class PaymentStatus(models.Model):
  name = models.CharField(max_length=30)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.name
  
  class Meta:
    verbose_name_plural = 'Payment Status'
  

class Bill(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  name = models.CharField(max_length=30)
  bill_type = models.CharField(max_length=25, null=True, blank=True)
  description = models.TextField(null=True, blank=True)
  due_date = models.DateField()
  amount_payable = models.FloatField()
  amount = models.FloatField()
  payment_status = models.ForeignKey('PaymentStatus', on_delete=models.CASCADE)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.name
  
  class Meta:
    ordering = ['payment_status', 'due_date']
    

class PaymentMethod(models.Model):
  bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
  method_name = models.CharField(max_length=25)
  amount = models.FloatField()
  fee_amount = models.FloatField(default=0)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.method_name
  

class USettings(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  auto_recurring = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return self.auto_recurring
  
  class Meta:
    verbose_name_plural = 'USettings'