from django.core.management.base import BaseCommand
from django.db.models import Subquery, OuterRef, Exists
from billstracker.models import Bill, BillDetail, Payment

class Command(BaseCommand):
    help = "Clear all records from Bill, BillDetail, Payment"

    def handle(self, *args, **kwargs):
        confirm = input("⚠️ Are you sure you want to delete all records from the table? (yes/no): ")

        if confirm.lower() == "yes":
            bill_deleted_count, _ = Bill.objects.all().delete()
            billdetail_deleted_count, _ = BillDetail.objects.all().delete()
            payment_deleted_count, _ = Payment.objects.all().delete()
            
            deleted_count = bill_deleted_count + billdetail_deleted_count + payment_deleted_count
            
            self.stdout.write(self.style.SUCCESS(f"✅ Successfully deleted {deleted_count} records."))
        else:
            self.stdout.write(self.style.WARNING("❌ Operation cancelled."))