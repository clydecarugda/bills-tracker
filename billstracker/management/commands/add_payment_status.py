from django.core.management.base import BaseCommand
from django.db.models import Subquery, OuterRef, Exists
from billstracker.models import PaymentStatus

class Command(BaseCommand):
    help = "Add default date for payment status table"

    def handle(self, *args, **kwargs):
      payment_status = ['Pending', 'Paid', 'Partially Paid']

      total_created = 0
      for status in payment_status:
        obj, created = PaymentStatus.objects.get_or_create(
          name = status
        )
        
        if created:
          total_created += 1

      self.stdout.write(self.style.SUCCESS(f"Successfully created {total_created} payment status."))