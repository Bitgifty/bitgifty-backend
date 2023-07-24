from django.urls import path

from .import views

urlpatterns = [
    path('', views.PayoutListCreateAPIView.as_view(), name='payout'),
    path('<int:pk>/', views.PayoutDetailAPIView.as_view(), name="payout_detail"),
]
