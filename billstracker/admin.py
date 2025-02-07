from django.contrib import admin
from .models import Payment, PaymentStatus, BillDetail, Bill, BillCategory, UserProfile, MoneyAccount, AccountGroup

admin.site.register(Payment)
admin.site.register(PaymentStatus)
admin.site.register(BillDetail)
admin.site.register(Bill)
admin.site.register(BillCategory)
admin.site.register(UserProfile)
admin.site.register(AccountGroup)
admin.site.register(MoneyAccount)