"""BinanceGift URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import re_path
from django.conf.urls.static import static
from dj_rest_auth.views import PasswordResetConfirmView
from dj_rest_auth.registration.views import VerifyEmailView

from accounts.views import CustomKoxLogin

schema_view = get_schema_view(
   openapi.Info(
      title="Bitgifty API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/login/', CustomKoxLogin.as_view(), name='knox_login'),
    # path('auth/', include('knox.urls')),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/account-confirm-email/', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    path('auth/password/password-reset-confirm/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),  
    path('', include('transactions.urls')),
    
    path('auth/registration/', include('dj_rest_auth.registration.urls')),

    path('gift_cards/', include('giftCards.urls')),
    
    path('payouts/', include('payouts.urls')),

    path('payouts/', include('payouts.urls')),

    path('swap/', include('swap.urls')),

    path('utilities/', include('utilities.urls')),

    path('wallets/', include('wallets.urls')),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
