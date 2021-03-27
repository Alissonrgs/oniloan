"""oniloan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# django
from django.conf import settings
from django.contrib import admin
from django.urls import include
from django.urls import path

# third party
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView


urlpatterns = [
    # admin
    path('admin/', admin.site.urls),

    # jwt auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # loans
    path('api/', include(('loans.urls', 'loans'), namespace='loans'))
]

if settings.DEBUG:
    if 'drf_yasg' in settings.INSTALLED_APPS:
        from drf_yasg import openapi
        from drf_yasg.views import get_schema_view
        from rest_framework import permissions

        schema_view = get_schema_view(
            openapi.Info(
                title="Oniloan API",
                default_version='v1',
                description="Oniloan Description",
                terms_of_service="https://www.google.com/policies/terms/",
                contact=openapi.Contact(email=settings.DEFAULT_FROM_EMAIL),
                license=openapi.License(name="BSD License")
            ),
            public=True,
            permission_classes=[permissions.AllowAny])

        urlpatterns += [
            # url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
            path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
            path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
        ]

    if 'silk' in settings.INSTALLED_APPS:
        urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
