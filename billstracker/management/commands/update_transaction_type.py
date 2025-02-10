from django.core.management.base import BaseCommand
from billstracker.models import Payment

class Command(BaseCommand):
    help = "Update Payment records with null transaction type but with bill_id to Bills Payment"

    def handle(self, *args, **kwargs):
        batch_size = 500  # Process records in batches
        payments = Payment.objects.filter(transaction_type__isnull=True)
        
        total_updated = 0
        for payment in payments.iterator():
          if payment.transaction_type is None and payment.bill is not None:
            payment.transaction_type = 'Bill Payment'
            payment.save()
            total_updated += 1
            
            if total_updated % batch_size == 0:
                self.stdout.write(f"Updated {total_updated} records...")
        
        self.stdout.write(self.style.SUCCESS(f"Successfully updated {total_updated} payment records."))
