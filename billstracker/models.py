from django.db import models
from django.contrib.auth.models import User


class PaymentStatus(models.Model):
  name = models.CharField(max_length=30)
  
  def __str__(self):
    return self.name
  

class Bills(models.Model):
  user_id = models.ForeignKey('User', on_delete=models.CASCADE)
  name = models.CharField(max_length=30)
  bill_type = models.CharField(max_length=25, null=True, blank=True)
  description = models.TextField(null=True, blank=True)
  due_date = models.DateField(auto_now_add=True)
  amount = models.FloatField(default=0)
  payment_status = models.ForeignKey('PaymentStatus', on_delete=models.CASCADE)
  recurring = models.BooleanField(default=False)
  
  def __str__(self):
    return self.name
  
  class Meta:
    ordering = ['due_date']