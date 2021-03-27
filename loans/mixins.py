# third party
from rest_framework.generics import get_object_or_404

# local
from .models import Loan


class LoanMixin:

    lookup_url_kwarg = 'loan_pk'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(client=self.request.user)
        return queryset


class PaymentMixin:

    def dispatch(self, request, *args, **kwargs):
        self.loan = get_object_or_404(Loan, pk=kwargs.get('loan_pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(loan=self.loan)
        if not self.request.user.is_staff:
            return queryset.filter(client=self.request.user)
        return queryset
