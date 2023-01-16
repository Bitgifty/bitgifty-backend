import os

from django.shortcuts import render

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from .serializers import WalletSerializer
from .models import Wallet

from core.utils import Blockchain
# Create your views here.


class WalletAPIView(generics.GenericAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()

    def get(self, request):
        """Confirms if a payment is legit"""
        try:
            user = request.user
            wallet_address = user.wallet_address

            client = Blockchain(os.getenv("TATUM_API_KEY"), os.getenv("BIN_KEY"), os.getenv("BIN_SECRET"))
            wallet_info = client.get_wallet_info(wallet_address, "tron")
            return Response(wallet_info, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": exception}, status=status.HTTP_400_BAD_REQUEST)
