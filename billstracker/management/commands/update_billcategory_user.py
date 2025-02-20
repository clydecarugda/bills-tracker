from django.core.management.base import BaseCommand
from django.db.models import Subquery, OuterRef, Exists
from billstracker.models import BillCategory, BillDetail, User

class Command(BaseCommand):
    help = "Update BillCategory user field based on associated BillDetail entries."

    def handle(self, *args, **kwargs):
        categories = BillCategory.objects.filter(user__isnull=True)

        total_updated = 0
        for category in categories:
            # Get the first BillDetail associated with the category
            bill_detail = BillDetail.objects.filter(category=category).first()

            if bill_detail and bill_detail.user:
                category.user = bill_detail.user
                category.save()
                total_updated += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully updated {total_updated} BillCategory records."))