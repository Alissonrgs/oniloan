# python
import uuid
from decimal import Decimal

# django
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

# third party
from dateutil.relativedelta import relativedelta
from django_extensions.db.models import TimeStampedModel

# local
from .constants import AWAITING_PAYMENT
# from .constants import IN_ANALYSIS
from .constants import LOAN_FINANCING_CHOICES
# from .constants import LOAN_STATUS_CHOICES
from .constants import PAID
from .constants import PAYMENT_STATUS_CHOICES
from .constants import PRICE_SYSTEM
from .constants import SAC_SYSTEM
from .utils import make_amortization
from .utils import make_amount_due
from .utils import make_installment


class Loan(TimeStampedModel):

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)

    client = models.ForeignKey(
        User, on_delete=models.CASCADE)

    ip_address = models.GenericIPAddressField(
        _('Endereço de IP'), unpack_ipv4=True, null=True)

    bank = models.CharField(
        _('Banco'), max_length=256)

    value = models.DecimalField(
        _('Valor Nominal'), decimal_places=2, max_digits=18,
        validators=[MinValueValidator(Decimal('0.01'))])

    amount_due = models.DecimalField(
        _('Valor Total Devido'), decimal_places=2, max_digits=18, null=True,
        validators=[MinValueValidator(Decimal('0.00'))])

    interest_rate = models.DecimalField(
        _('Taxa de Juros'), decimal_places=2, max_digits=5,
        validators=[MinValueValidator(Decimal('0.01'))])

    period = models.PositiveIntegerField(
        _('Período'))

    financing = models.PositiveIntegerField(
        _('Tipo de Financiamento'), choices=LOAN_FINANCING_CHOICES, default=PRICE_SYSTEM)

    # status = models.PositiveIntegerField(
    #     _('status'), choices=LOAN_STATUS_CHOICES, default=IN_ANALYSIS)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.bank} - {self.get_financing_display()}'

    def make_balance_due(self) -> float:
        """
        calculate balance due
        """
        paid = self.payment_set.aggregate(paid=Sum('value', filter=Q(status=PAID))).get('paid')
        if paid:
            return self.amount_due - paid
        return self.amount_due


class Payment(TimeStampedModel):

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)

    client = models.ForeignKey(
        User, on_delete=models.CASCADE)

    loan = models.ForeignKey(
        Loan, on_delete=models.CASCADE)

    value = models.DecimalField(
        _('Valor'), decimal_places=2, max_digits=18,
        validators=[MinValueValidator(Decimal('0.01'))])

    interest_amount = models.DecimalField(
        _('Juros'), decimal_places=2, max_digits=18,
        validators=[MinValueValidator(Decimal('0.00'))])

    amortization = models.DecimalField(
        _('Amortização sobre saldo devedor'), decimal_places=2, max_digits=18,
        validators=[MinValueValidator(Decimal('0.00'))])

    due_date = models.DateTimeField(
        _('Data do Vencimento'))

    pay_date = models.DateTimeField(
        _('Data do pagamento'), null=True)

    status = models.PositiveIntegerField(
        _('status'), choices=PAYMENT_STATUS_CHOICES, default=AWAITING_PAYMENT)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'R$ {self.value:.2f} - {self.get_status_display()}'


@receiver(post_save, sender=Loan)
def loan_post_save(sender, instance, created, **kwargs):
    if not created:
        return

    instance.amount_due = make_amount_due(
        instance.financing, instance.value, instance.interest_rate, instance.period)
    instance.save(update_fields=['amount_due'])

    value = float(instance.value)
    interest_rate = float(instance.interest_rate)
    period = instance.period
    due_date = now()

    payments_bulk = []

    if instance.financing == PRICE_SYSTEM:
        installment = make_installment(value, interest_rate, period)

        for p in range(period):
            due_date += relativedelta(months=1)
            interest_amount = round(value * interest_rate, 2)
            amortization = round(installment - interest_amount, 2)
            value -= amortization

            payment = Payment(
                client=instance.client,
                loan=instance,
                value=installment,
                due_date=due_date,
                interest_amount=interest_amount,
                amortization=amortization)
            payments_bulk.append(payment)

    elif instance.financing == SAC_SYSTEM:
        amortization = make_amortization(value, period)

        for p in range(period):
            due_date += relativedelta(months=1)
            interest_amount = round(value * interest_rate, 2)
            installment = amortization + interest_amount
            value -= amortization

            payment = Payment(
                client=instance.client,
                loan=instance,
                value=installment,
                due_date=due_date,
                interest_amount=interest_amount,
                amortization=amortization)
            payments_bulk.append(payment)

    if payments_bulk:
        Payment.objects.bulk_create(payments_bulk)
