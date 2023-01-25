from django.urls import path

from . import views

urlpatterns = [
    path('', views.WalletAPIView.as_view()),
    path('<str:network>/', views.WalletDetailAPIView.as_view()),
]