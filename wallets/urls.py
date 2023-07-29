from django.urls import path

from . import views

urlpatterns = [
    path('', views.WalletAPIView.as_view()),
    path('fix', views.recreate_wallet),
    path('fix_qr', views.recreate_qr),
    path('create_naira/', views.create_naira_wallet),
    path('<str:network>/', views.WalletDetailAPIView.as_view()),
    
]
