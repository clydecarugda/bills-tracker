from django.contrib import admin
from .models import Payment, PaymentStatus, BillDetail, Bill, UserProfile, MoneyAccount, AccountGroup, AuditLog
from .models import Category, BillCategory

admin.site.register(Payment)
admin.site.register(PaymentStatus)
admin.site.register(BillDetail)
admin.site.register(Bill)
admin.site.register(UserProfile)
admin.site.register(AccountGroup)
admin.site.register(MoneyAccount)
admin.site.register(AuditLog)
admin.site.register(Category)
admin.site.register(BillCategory)