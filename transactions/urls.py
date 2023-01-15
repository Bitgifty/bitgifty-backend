from django.urls import path

from . import views

urlpatterns = [
    path('', views.TransactionListAPIView.as_view()),
]