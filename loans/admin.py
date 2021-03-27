# django
from django.contrib import admin

# local
from .models import Loan
from .models import Payment


class LoanAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'ip_address', 'value', 'amount_due', 'interest_rate', 'financing',
                    'created', 'modified']


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'loan', 'value', 'interest_amount', 'amortization',
                    'due_date', 'pay_date', 'status', 'created']


admin.site.register(Loan, LoanAdmin)
admin.site.register(Payment, PaymentAdmin)
