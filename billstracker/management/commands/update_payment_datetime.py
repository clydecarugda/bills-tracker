from django.core.management.base import BaseCommand
from billstracker.models import Payment

class Command(BaseCommand):
    help = "Update Payment records with blank payment_date_time using the values from create_at"

    def handle(self, *args, **kwargs):
        batch_size = 500  # Process records in batches
        payments = Payment.objects.filter(payment_date_time__isnull=True)
        
        total_updated = 0
        for payment in payments.iterator():
            payment.payment_date_time = payment.created_at
            payment.save()
            total_updated += 1
            
            if total_updated % batch_size == 0:
                self.stdout.write(f"Updated {total_updated} records...")
        
        self.stdout.write(self.style.SUCCESS(f"Successfully updated {total_updated} payment records."))