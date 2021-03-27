# python
from decimal import Decimal
from typing import Union

# project
from .constants import PRICE_SYSTEM
from .constants import SAC_SYSTEM


def make_installment(value: Union[Decimal, float], interest_rate: Union[Decimal, float], period: int) -> float:
    """
    fixed installments for price system
    """
    interest_rate = float(interest_rate)

    data = (1 + interest_rate) ** period
    data = (data * interest_rate) / (data - 1)
    return round(float(value) * data, 2)


def make_amortization(value: Union[Decimal, float], period: int) -> float:
    """
    fixed amortization for SAC system
    """
    return round(float(value) / period)


def make_amount_due(financing: int, value: float, interest_rate: float, period: int) -> float:
    if financing == PRICE_SYSTEM:
        installment = make_installment(value, interest_rate, period)

        return round(installment * period, 2)

    elif financing == SAC_SYSTEM:
        amount_due = 0
        amortization = make_amortization(value, period)

        for p in range(period):
            interest_amount = round(value * interest_rate, 2)
            installment = amortization + interest_amount
            value -= amortization
            amount_due += installment
        return round(amount_due, 2)

    return 0
