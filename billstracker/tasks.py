from celery import shared_task
from django.core.mail import send_mail
from datetime import datetime
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@shared_task
def send_due_date_reminder():
  from billstracker.models import Bill
  
  today = datetime.now().date()
  bills_due_today = Bill.objects.filter(
    Q(due_date__lte=today) &
    Q(payment_status__in=[1, 3]))
  
  subject = "📢 Reminder: Your Bill is Due!"
  from_email = 'clydeocarugda@gmail.com'
  
  for bill in bills_due_today:
    html_message = render_to_string("emails/bill_reminder.html", {"username": bill.user.first_name, "bill_name": bill.bill_detail.name, "due_date": bill.due_date, "bill_id": bill.id, "detail_id": bill.bill_detail.id })
    plain_message = strip_tags(html_message)
    
    if bill.user.email:
      send_mail(
        subject=subject,
        message=plain_message,
        from_email=from_email,
        recipient_list=[bill.user.email],
        fail_silently=False,
        html_message=html_message
      )
      
@shared_task
def send_test_email(name="send_test_email_task"):
  send_mail(
    subject="Test Email from Django & Celery",
    message="This is a test email to confirm Celery is working well",
    from_email="bills-tracker@gmail.com",
    recipient_list=['clydeocarugda@gmail.com'],
    fail_silently=False
  )
  
  return "Email Sent!"