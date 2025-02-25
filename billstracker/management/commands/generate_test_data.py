import random
import uuid
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from billstracker.models import (
    AccountGroup, Category, MoneyAccount,
    PaymentStatus, BillCategory, BillDetail, Bill, Payment
)

class Command(BaseCommand):
    help = "Populate the database with realistic test data"

    def handle(self, *args, **kwargs):
        users = User.objects.all()

        if not users.exists():
            self.stdout.write(self.style.WARNING("No users found! Create users first."))
            return

        for user in users:
            self.create_account_groups(user)
            self.create_categories(user)
            self.create_money_accounts(user)
            self.create_bill_categories(user)
            self.create_bill_details(user)
            self.create_bills(user)
            self.create_payments(user)

        self.stdout.write(self.style.SUCCESS("Test data successfully populated!"))

    def create_account_groups(self, user):
        account_groups = ["Savings", "Investments", "Cash", "Emergency Fund", "Business Account"]
        for name in account_groups:
            AccountGroup.objects.create(user=user, name=name)

    def create_categories(self, user):
        categories = [
            ("Salary", "Income"),
            ("Freelance", "Income"),
            ("Groceries", "Expense"),
            ("Rent", "Expense"),
            ("Utilities", "Expense"),
            ("Entertainment", "Expense"),
            ("Insurance", "Expense"),
            ("Transportation", "Expense"),
            ("Healthcare", "Expense"),
            ("Miscellaneous", "Expense")
        ]
        for name, category_type in categories:
            Category.objects.create(user=user, name=name, category_type=category_type)

    def create_money_accounts(self, user):
        account_groups = list(AccountGroup.objects.filter(user=user))
        money_accounts = [
            ("Checking Account", 2000),
            ("Savings Account", 5000),
            ("Credit Card", -1000),
            ("Investment Portfolio", 15000),
            ("Business Account", 8000)
        ]
        for name, amount in money_accounts:
            MoneyAccount.objects.create(
                user=user,
                account_group=random.choice(account_groups),
                name=name,
                amount=amount,
                description=f"{name} account for {user.username}"
            )

    def create_bill_categories(self, user):
        bill_categories = ["Electricity", "Water", "Internet", "Rent", "Subscription", "Loan", "Phone Bill", "Insurance"]
        for name in bill_categories:
            BillCategory.objects.create(user=user, name=name)

    def create_bill_details(self, user):
        categories = list(Category.objects.filter(user=user, category_type="Expense"))
        bill_names = [
            "Electric Bill", "Water Bill", "Netflix Subscription", "Gym Membership", "Home Loan EMI",
            "Car Loan EMI", "Phone Bill", "Health Insurance Premium", "Car Insurance Premium",
            "Spotify Subscription", "Amazon Prime Subscription", "Gas Bill", "Credit Card Payment"
        ]
        recurring_types = ["one-time", "monthly", "yearly"]

        for name in bill_names:
            BillDetail.objects.create(
                user=user,
                name=name,
                category=random.choice(categories),
                description=f"{name} for {user.username}",
                is_recurring=random.choice(recurring_types)
            )

    def create_bills(self, user):
        bill_details = list(BillDetail.objects.filter(user=user))
        payment_statuses = PaymentStatus.objects.all()

        for _ in range(random.randint(50, 100)):
            amount = random.randint(50, 3000)  # More realistic bill amounts
            Bill.objects.create(
                user=user,
                bill_detail=random.choice(bill_details),
                due_date=datetime.today() + timedelta(days=random.randint(1, 60)),
                amount=amount,
                amount_payable=amount,  # Ensuring the same amount
                payment_status=random.choice(payment_statuses)
            )

    def create_payments(self, user):
        bills = list(Bill.objects.filter(user=user))
        accounts = list(MoneyAccount.objects.filter(user=user))
        categories = list(Category.objects.filter(user=user))

        for _ in range(random.randint(30, 80)):
            bill = random.choice(bills)
            transaction_type = random.choice(["Income", "Expense"])
            Payment.objects.create(
                user=user,
                bill=bill if transaction_type == "Expense" else None,
                account=random.choice(accounts),
                payment_reference=str(uuid.uuid4()),
                transaction_type=transaction_type,
                category=random.choice(categories),
                amount=random.randint(50, 2000) if transaction_type == "Income" else bill.amount,
                fee_amount=random.randint(10, 25) if transaction_type == "Expense" else 0,
                note=f"{'Received' if transaction_type == 'Income' else 'Paid'} {bill.bill_detail.name if transaction_type == 'Expense' else 'Income'}",
                payment_date_time=datetime.now() - timedelta(days=random.randint(1, 30))
            )
