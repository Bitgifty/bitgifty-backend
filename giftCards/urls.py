from django.urls import path

from . import views

urlpatterns = [
    path('', views.GiftCardAPIView.as_view()),
    path('<int:pk>/', views.GiftCardDetailView.as_view()),
]