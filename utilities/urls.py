from django.urls import path

from . import views

urlpatterns = [
    path('buy-data/', views.BuyDataAPIView.as_view()),
    path('buy-airtime/', views.BuyAirtimeAPIView.as_view()),
    path('buy-cable/', views.BuyCableAPIView.as_view()),
    path('buy-electricity/', views.BuyElectricityAPIView.as_view()),
    path('naira/<str:using>/', views.SwapRateAPIView.as_view()),
    path('cable/', views.CableAPIView.as_view()),
    path('cable-plan/', views.CablePlanAPIView.as_view()),
    path('network/', views.NetworkAPIView.as_view()),
    path('data-plan/', views.DataPlanAPIView.as_view()),
    path('disco/', views.DiscoAPIView.as_view()),
]
