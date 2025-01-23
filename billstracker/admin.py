from django.contrib import admin
from .models import PaymentMethod, PaymentStatus, Bill, USettings, BillCategory

admin.site.register(PaymentMethod)
admin.site.register(PaymentStatus)
admin.site.register(Bill)
admin.site.register(BillCategory)
admin.site.register(USettings)