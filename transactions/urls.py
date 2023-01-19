from django.urls import path

from . import views

urlpatterns = [
    path('transactions/', views.TransactionListAPIView.as_view()),
    path('withdraw/', views.WithdrawAPIView.as_view()),
]