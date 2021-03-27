# third party
from rest_framework import serializers

# project
from core.constants import DATETIME_FORMAT
from core.serializers import UserSerializer

# local
from .models import Loan
from .models import Payment


# Loans

class LoanCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loan
        fields = ['client', 'bank', 'value', 'interest_rate', 'period', 'financing']


class LoanSerializer(serializers.ModelSerializer):

    created = serializers.DateTimeField(format=DATETIME_FORMAT, read_only=True)
    modified = serializers.DateTimeField(format=DATETIME_FORMAT, read_only=True)
    client = UserSerializer()
    value = serializers.SerializerMethodField()
    amount_due = serializers.SerializerMethodField()
    interest_rate = serializers.SerializerMethodField()
    balance_due = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = '__all__'

    def get_value(self, obj):
        return f'R$ {obj.value:.2f}'

    def get_amount_due(self, obj):
        return f'R$ {obj.amount_due:.2f}'

    def get_interest_rate(self, obj):
        return f'{100.0 * float(obj.interest_rate):.2f}%'

    def get_balance_due(self, obj):
        return f'R$ {obj.make_balance_due():.2f}'


# Payments

class PaymentSerializer(serializers.ModelSerializer):

    created = serializers.DateTimeField(format=DATETIME_FORMAT, read_only=True)
    modified = serializers.DateTimeField(format=DATETIME_FORMAT, read_only=True)
    value = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Payment
        fields = '__all__'

    def get_value(self, obj):
        return f'R$ {obj.value:.2f}'


class PaymentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ['status']
