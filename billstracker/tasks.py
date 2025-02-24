from celery import shared_task
from django.core.mail import send_mail
from datetime import datetime

@shared_task
def send_due_date_reminder():
  from billstracker.models import Bill
  
  today = datetime.now().date()
  bills_due_today = Bill.objects.filter(due_date=today)
  
  for bill in bills_due_today:
    if bill.user.email:
      send_mail(
        'Bill Due Reminder',
        f'Hello {bill.user.first_name}, your bill "{bill.bill_detail.name} is due today.',
        'clydeocarugda@gmail.com',
        [bill.user.email],
        fail_silently = False,
        )
      
@shared_task
def send_test_email(name="send_test_email_task"):
  send_mail(
    subject="Test Email from Django & Celery",
    message="This is a test email to confirm Celery is working well",
    from_email="clydeocarugda@gmail.com",
    recipient_list=['clydeocarugda@gmail.com'],
    fail_silently=False
  )
  
  return "Email Sent!"