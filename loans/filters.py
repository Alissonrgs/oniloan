# third party
import django_filters

# local
from .models import Loan
from .models import Payment


class LoanFilterSet(django_filters.FilterSet):

    class Meta:
        model = Loan
        fields = ['created', 'modified', 'client', 'ip_address', 'financing']


class PaymentFilterSet(django_filters.FilterSet):

    class Meta:
        model = Payment
        fields = ['created', 'modified', 'status']
