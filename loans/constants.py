from django.utils.translation import gettext_lazy as _

PRICE_SYSTEM = 1
SAC_SYSTEM = 2

LOAN_FINANCING_CHOICES = (
    (PRICE_SYSTEM, _('Sistema Price')),
    (SAC_SYSTEM, _('Sistema SAC'))
)

LOAN_FINANCING_MAP = dict(LOAN_FINANCING_CHOICES)

IN_ANALYSIS = 1
APPROVED = 2
DISAPPROVED = 3

LOAN_STATUS_CHOICES = (
    (IN_ANALYSIS, _('Em Análise')),
    (APPROVED, _('Aprovado')),
    (DISAPPROVED, _('Reprovado'))
)

AWAITING_PAYMENT = 1
PROCESSING = 2
PAID = 3
DUE = 4
CANCELED = 5

PAYMENT_STATUS_CHOICES = (
    (AWAITING_PAYMENT, _('Aguardando Pagamento')),
    (PROCESSING, _('Processando')),
    (PAID, _('Pago')),
    (DUE, _('Vencido')),
    (CANCELED, _('Cancelado'))
)
