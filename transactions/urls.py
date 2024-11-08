from django.urls import path

from . import views

urlpatterns = [
    path('transactions/fiat/', views.FiatTransactionListAPIView.as_view()),
    path('transactions/<str:network>/', views.TransactionListAPIView.as_view()),
    path('withdraw/', views.WithdrawAPIView.as_view()),
]