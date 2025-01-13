from django.db import models
from django.contrib.auth.models import User


class PaymentStatus(models.Model):
  name = models.CharField(max_length=30)
  
  def __str__(self):
    return self.name
  
  class Meta:
    verbose_name_plural = 'Payment Status'
  

class Bill(models.Model):
  user_id = models.ForeignKey(User, on_delete=models.CASCADE)
  name = models.CharField(max_length=30)
  bill_type = models.CharField(max_length=25, null=True, blank=True)
  description = models.TextField(null=True, blank=True)
  due_date = models.IntegerField(choices=[(i, i) for i in range (1, 32)], verbose_name='Due Date')
  amount = models.FloatField(default=0)
  payment_status = models.ForeignKey('PaymentStatus', on_delete=models.CASCADE)
  recurring = models.BooleanField(default=False)
  bill_month = models.IntegerField(choices=[(i, i) for i in range (1, 13)], verbose_name='Month')
  
  def __str__(self):
    return self.name
  
  class Meta:
    ordering = ['due_date']
    

class PaymentMethod(models.Model):
  bill_id = models.ForeignKey(Bill, on_delete=models.CASCADE)
  method_name = models.CharField(max_length=25)
  amount = models.FloatField()
  fee_amount = models.FloatField(default=0)
  
  def __str__(self):
    return self.method_name
  

class USettings(models.Model):
  user_id = models.ForeignKey(User, on_delete=models.CASCADE)
  auto_recurring = models.BooleanField(default=False)
  
  def __str__(self):
    return self.auto_recurring
  
  class Meta:
    verbose_name_plural = 'USettings'