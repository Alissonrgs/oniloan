# python
from decimal import Decimal
from model_bakery import baker

# django
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from django.urls import reverse

# third party
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

# project
from core.constants import DATETIME_FORMAT
from core.serializers import UserSerializer

# local
from loans.models import Loan
from loans.models import Payment
from loans.constants import PRICE_SYSTEM
from loans.constants import SAC_SYSTEM
from .utils import utc_to_local

User = get_user_model()


class BaseAPITestCase(APITestCase):

    def setUp(self):
        # admin
        self.admin = baker.make(User, is_staff=True, is_superuser=True)
        self.admin_token = RefreshToken.for_user(self.admin).access_token
        self.admin_headers = {'REMOTE_ADDR': '192.168.0.10'}

        # client
        self.user = baker.make(User)
        self.headers = {'REMOTE_ADDR': '192.168.0.20'}
        self.token = RefreshToken.for_user(self.user).access_token

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')


class BaseLoanAPITestCase(BaseAPITestCase):

    def setUp(self):
        super().setUp()

        data_price = {'client': self.user,
                      'bank': 'testbank',
                      'value': 20000.00,
                      'interest_rate': 0.04,
                      'period': 8,
                      'financing': PRICE_SYSTEM}
        self.loan_price = Loan.objects.create(**data_price)

        user = baker.make(User)
        data_sac = {'client': user,
                    'bank': 'testbank',
                    'value': 120000.00,
                    'interest_rate': 0.05,
                    'period': 10,
                    'financing': SAC_SYSTEM}
        self.loan_sac = Loan.objects.create(**data_sac)


class TestLoanCreateAPIView(BaseAPITestCase):

    def get_url(self):
        return reverse('loans:create')

    def test_create_loan_without_authentication(self):
        self.client.logout()

        data = {'client': self.user.id,
                'bank': 'testbank',
                'value': 20000.00,
                'interest_rate': 0.04,
                'period': 8,
                'financing': PRICE_SYSTEM}
        response = self.client.post(self.get_url(), data, **self.admin_headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('detail'), 'As credenciais de autenticação não foram fornecidas.')
        self.assertEqual(Loan.objects.count(), 0)
        self.assertEqual(Payment.objects.count(), 0)

    def test_create_loan_by_client(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        data = {'client': self.user.id,
                'bank': 'testbank',
                'value': 20000.00,
                'interest_rate': 0.04,
                'period': 8,
                'financing': PRICE_SYSTEM}
        response = self.client.post(self.get_url(), data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('detail'), 'Você não tem permissão para executar essa ação.')
        self.assertEqual(Loan.objects.count(), 0)
        self.assertEqual(Payment.objects.count(), 0)

    def test_create_loan_by_admin(self):
        data = {'client': self.user.id,
                'bank': 'testbank',
                'value': 20000.00,
                'interest_rate': 0.04,
                'period': 8,
                'financing': PRICE_SYSTEM}
        response = self.client.post(self.get_url(), data, **self.admin_headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Loan.objects.count(), 1)
        self.assertEqual(Payment.objects.count(), 8)

        loan = Loan.objects.get()
        self.assertEqual(loan.ip_address, '192.168.0.10')
        self.assertEqual(loan.amount_due, Decimal('23764.48'))

    def test_create_loan_with_empty_data(self):
        reponse_error = {
            'client': ['Este campo é obrigatório.'],
            'bank': ['Este campo é obrigatório.'],
            'value': ['Este campo é obrigatório.'],
            'interest_rate': ['Este campo é obrigatório.'],
            'period': ['Este campo é obrigatório.']}

        data = {}
        response = self.client.post(self.get_url(), data, **self.admin_headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), reponse_error)
        self.assertEqual(Loan.objects.count(), 0)
        self.assertEqual(Payment.objects.count(), 0)

    def test_create_loan_with_wrong_data(self):
        reponse_error = {
            'client': ['Pk inválido "10" - objeto não existe.'],
            'value': ['Certifque-se de que este valor seja maior ou igual a 0.01.'],
            'interest_rate': ['Certifque-se de que este valor seja maior ou igual a 0.01.'],
            'period': ['Um número inteiro válido é exigido.'],
            'financing': ['"0" não é um escolha válido.']}

        data = {'client': 10,
                'bank': 'testbank',
                'value': 0.00,
                'interest_rate': -0.01,
                'period': 'a',
                'financing': 0}
        response = self.client.post(self.get_url(), data, **self.admin_headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), reponse_error)
        self.assertEqual(Loan.objects.count(), 0)
        self.assertEqual(Payment.objects.count(), 0)


class TestLoanListAPIView(BaseLoanAPITestCase):

    def get_url(self):
        return reverse('loans:list')

    def test_list_loan_without_authentication(self):
        self.client.logout()

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('detail'), 'As credenciais de autenticação não foram fornecidas.')

    def test_list_loan_by_client(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results')), 1)

    def test_list_loan_by_admin(self):
        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results')), 2)


class TestLoanRetrieveAPIView(BaseLoanAPITestCase):

    maxDiff = None

    def get_url(self, loan):
        return reverse('loans:retrieve', args=[loan.id])

    def serializer_format(self, loan):
        return {
            **model_to_dict(loan),
            'id': str(loan.id),
            'created': utc_to_local(loan.created).strftime(DATETIME_FORMAT),
            'modified': utc_to_local(loan.modified).strftime(DATETIME_FORMAT),
            'client': UserSerializer(loan.client).data,
            'value': f'R$ {loan.value:.2f}',
            'amount_due': f'R$ {loan.amount_due:.2f}',
            'interest_rate': f'{100.0 * float(loan.interest_rate):.2f}%',
            'balance_due': f'R$ {loan.make_balance_due():.2f}'}

    def test_retrieve_loan_price_without_authentication(self):
        self.client.logout()

        response = self.client.get(self.get_url(self.loan_price))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('detail'), 'As credenciais de autenticação não foram fornecidas.')

    def test_retrieve_loan_price_by_client(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response_json = self.serializer_format(self.loan_price)

        response = self.client.get(self.get_url(self.loan_price))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.json(), response_json)

    def test_retrieve_loan_sac_by_client_without_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        response = self.client.get(self.get_url(self.loan_sac))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json().get('detail'), 'Não encontrado.')

    def test_retrieve_loan_price_by_admin(self):
        response = self.client.get(self.get_url(self.loan_price))
        response_json = self.serializer_format(self.loan_price)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.json(), response_json)

    def test_retrieve_loan_sac_by_admin(self):
        response = self.client.get(self.get_url(self.loan_sac))
        response_json = self.serializer_format(self.loan_sac)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.json(), response_json)


class TestPaymentListAPIView(BaseLoanAPITestCase):

    def get_url(self, loan):
        return reverse('loans:payments-list', args=[loan.id])

    def test_list_loan_price_payments_without_authentication(self):
        self.client.logout()

        response = self.client.get(self.get_url(self.loan_price))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('detail'), 'As credenciais de autenticação não foram fornecidas.')

    def test_list_loan_price_payment_by_client(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        response = self.client.get(self.get_url(self.loan_price))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results')), 8)

    def test_list_loan_sac_payment_by_client_without_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        response = self.client.get(self.get_url(self.loan_sac))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('detail'), 'Você não tem permissão para executar essa ação.')

    def test_list_loan_price_payment_by_admin(self):
        response = self.client.get(self.get_url(self.loan_price))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results')), 8)

    def test_list_loan_sac_payment_by_admin(self):
        response = self.client.get(self.get_url(self.loan_sac))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json().get('results')), 10)
