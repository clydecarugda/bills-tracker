from django.core.management.base import BaseCommand
from django.db.models import Subquery, OuterRef, Exists
from billstracker.models import MoneyCategory ,User

class Command(BaseCommand):
    help = "Add Income and Expense Category for each available user."

    def handle(self, *args, **kwargs):
      income_categories = ['Salary', 'Petty Cash', 'Bonus']
      expense_categories = ['Food', 'Pets', 'Transport', 'Apparel', 'Household', 'Gift']
      users = User.objects.all()

      total_created = 0
      for user in users:
        for category_name in income_categories:
          obj, created = MoneyCategory.objects.get_or_create(
            user = user,
            name = category_name,
            category_type = 'Income'
          )
          
          if created:
            total_created += 1
            
        for category_name in expense_categories:
          obj, created = MoneyCategory.objects.get_or_create(
            user = user,
            name = category_name,
            category_type = 'Expense'
          )
          
          if created:
            total_created += 1

      self.stdout.write(self.style.SUCCESS(f"Successfully created {total_created} categories."))