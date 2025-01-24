from django.contrib import admin
from .models import Payment, PaymentStatus, BillDetail, Bill, USettings, BillCategory

admin.site.register(Payment)
admin.site.register(PaymentStatus)
admin.site.register(BillDetail)
admin.site.register(Bill)
admin.site.register(BillCategory)
admin.site.register(USettings)