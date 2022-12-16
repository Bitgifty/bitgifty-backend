from django.urls import path

from . import views

urlpatterns = [
    path('', views.WalletAPIView.as_view()),
    path('<int:pk>/', views.WalletDetailView.as_view()),
]