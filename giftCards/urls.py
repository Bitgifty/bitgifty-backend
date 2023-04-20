from django.urls import path

from . import views

urlpatterns = [
    path('create/', views.GiftCardAPIView.as_view()),
    path('<int:pk>/', views.GiftCardDetailView.as_view()),
    path('redeem/', views.RedeemAPIView.as_view()),
]