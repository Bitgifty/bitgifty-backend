from django.urls import path
from . import views

urlpatterns = [
    path("", views.PointsAPIView.as_view()),
    path("<str:wallet_address>/", views.PointsDetailAPIView.as_view())
]
