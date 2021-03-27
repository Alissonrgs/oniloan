# django
from django.urls import include
from django.urls import path

# local
from . import views


urlpatterns = [
    path('loans/', include([
        path('', views.LoanListAPIView.as_view(), name='list'),
        path('create/', views.LoanCreateAPIView.as_view(), name='create'),
        path('preview/', views.LoanPreviewAPIView.as_view(), name='preview'),

        path('<loan_pk>/', include([
            path('', views.LoanRetrieveAPIView.as_view(), name='retrieve'),

            # loan payments
            path('payments/', views.PaymentListAPIView.as_view(), name='payments-list'),
            path('payments/<pk>/update/', views.PaymentUpdateAPIView.as_view(), name='payments-update')
        ]))
    ]))
]
