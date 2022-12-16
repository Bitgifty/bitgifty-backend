from django.shortcuts import render

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .serializers import WalletSerializer
from .models import Wallet
# Create your views here.


class WalletAPIView(ListCreateAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()


class WalletDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()
