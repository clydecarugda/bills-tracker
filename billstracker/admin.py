from django.contrib import admin
from .models import PaymentMethod, PaymentStatus, Bill, USettings

admin.site.register(PaymentMethod)
admin.site.register(PaymentStatus)
admin.site.register(Bill)
admin.site.register(USettings)