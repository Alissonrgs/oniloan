# python
import logging

# django
from django.utils.timezone import now
from django.utils.translation import gettext as _

# third party
from dateutil.relativedelta import relativedelta
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

# project
from core.utils import get_ip_address

# local
from .constants import LOAN_FINANCING_MAP
from .constants import PRICE_SYSTEM
from .constants import SAC_SYSTEM
from .filters import LoanFilterSet
from .filters import PaymentFilterSet
from .mixins import LoanMixin
from .mixins import PaymentMixin
from .models import Loan
from .models import Payment
from .permissions import LoanPermission
from .serializers import LoanCreateSerializer
from .serializers import LoanSerializer
from .serializers import PaymentSerializer
from .serializers import PaymentUpdateSerializer
from .utils import make_amortization
from .utils import make_installment

logger = logging.getLogger(__name__)


# Loan

class LoanCreateAPIView(CreateAPIView):
    """
    Loan Create

    * Requires authentication
    * Only admin users can access this view
    """

    queryset = Loan.objects.all()
    serializer_class = LoanCreateSerializer
    permission_classes = [*api_settings.DEFAULT_PERMISSION_CLASSES, IsAdminUser]

    def perform_create(self, serializer):
        ip_address = get_ip_address(self.request)

        serializer.save(ip_address=ip_address)


class LoanListAPIView(LoanMixin, ListAPIView):
    """
    Loan List

    * Requires authentication
    * Only client or admin users can access this view
    """

    queryset = Loan.objects.all()
    filter_class = LoanFilterSet
    serializer_class = LoanSerializer
    search_fields = [
        'client__username', 'bank']
    ordering_fields = [
        'created', 'modified']


class LoanRetrieveAPIView(LoanMixin, RetrieveAPIView):
    """
    Loan Retrieve

    * Requires authentication
    * Only client or admin users can access this view
    """

    queryset = Loan.objects.all()
    serializer_class = LoanSerializer


class LoanPreviewAPIView(APIView):
    """
    Loan Preview

    * Any users can access this view
    """

    permission_classes = [AllowAny]
    error_exception = {
        'financing': _('Não pode ser vazio, deve ser uma das opções "1" ou "2"'),
        'value': _('Não pode ser vazio, deve ser do tipo float positivo'),
        'interest_rate': _('Não pode ser vazio, deve ser um float positivo'),
        'period': _('Não pode ser vazio, deve ser um inteiro positivo')}

    def get(self, request, *args, **kwargs):
        data = request.GET

        # validation get data
        try:
            financing = int(data.get('financing'))
            assert financing in LOAN_FINANCING_MAP

            value = float(data.get('value'))
            interest_rate = float(data.get('interest_rate')) / 100.0
            period = int(data.get('period'))
        except (TypeError, AssertionError) as err:
            logger.error("LoanPreviewAPIView", err)
            raise ValidationError(self.error_exception)

        # loan preview payments
        due_date = now()
        loan_value = value
        amount_due = 0
        pyment_order = 1
        payments = []

        if financing == PRICE_SYSTEM:
            installment = make_installment(value, interest_rate, period)

            for p in range(period):
                due_date += relativedelta(months=1)
                interest_amount = round(value * interest_rate, 2)
                amortization = round(installment - interest_amount, 2)
                value -= amortization
                amount_due += installment

                payment = {
                    'payment': pyment_order,
                    'value': installment,
                    'due_date': due_date,
                    'interest_amount': interest_amount,
                    'amortization': amortization}
                payments.append(payment)
                pyment_order += 1

        elif financing == SAC_SYSTEM:
            amortization = make_amortization(value, period)

            for p in range(period):
                due_date += relativedelta(months=1)
                interest_amount = round(value * interest_rate, 2)
                installment = amortization + interest_amount
                value -= amortization
                amount_due += installment

                payment = {
                    'payment': pyment_order,
                    'value': installment,
                    'due_date': due_date,
                    'interest_amount': interest_amount,
                    'amortization': amortization}
                payments.append(payment)
                pyment_order += 1

        loan_preview = {
            'loan': {
                'financing': LOAN_FINANCING_MAP[financing],
                'value': loan_value,
                'interest_rate': interest_rate,
                'period': period,
                'amount_due': round(amount_due, 2)},
            'payments': payments}
        return Response(loan_preview)


# Payments

class PaymentListAPIView(PaymentMixin, ListAPIView):
    """
    Payment List

    * Requires authentication
    * Only client or admin users can access this view
    """

    queryset = Payment.objects.all()
    filter_class = PaymentFilterSet
    serializer_class = PaymentSerializer
    permission_classes = [*api_settings.DEFAULT_PERMISSION_CLASSES, LoanPermission]
    ordering_fields = [
        'created', 'modified', 'status']


class PaymentUpdateAPIView(PaymentMixin, UpdateAPIView):
    """
    Payment Update

    * Requires authentication
    * Only admin users can access this view
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentUpdateSerializer
    http_method_names = [u'patch', u'head', u'options', u'trace']
    permission_classes = [*api_settings.DEFAULT_PERMISSION_CLASSES, IsAdminUser]
