from django.urls import path

from . import views

urlpatterns = [
    path('', views.SwapAPIView.as_view()),
    path('naira/<str:using>/', views.SwapRateAPIView.as_view()),
    path('get_usdt/<str:using>/', views.GetUSDTAPIView.as_view()),
]
