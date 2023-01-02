from django.urls import path

from . import views

urlpatterns = [
    path('', views.TransactionAPIView.as_view()),
    path('<int:pk>/', views.TransactionDetailView.as_view()),
    path('/confirm/<int:pk>/', views.TransactionConfirmView.as_view()),
]