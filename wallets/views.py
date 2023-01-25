import os

from django.shortcuts import render

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from .serializers import WalletSerializer
from .models import Wallet

from core.utils import Blockchain
# Create your views here.


class WalletDetailAPIView(generics.GenericAPIView):
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()

    def get(self, request, network):
        """Confirms if a payment is legit"""
        try:
            network_mapping = {
                "bnb": "bsc",
                "bitcoin": "bitcoin",
                "celo": "celo",
                "ethereum": "ethereum",
                "tron": "tron"
            }
            user = request.user
            wallet_address = user.wallet_address
            network = network.lower()
            client = Blockchain(os.getenv("TATUM_API_KEY"), os.getenv("BIN_KEY"), os.getenv("BIN_SECRET"))
            wallet_info = client.get_wallet_info(wallet_address, network_mapping[network])
            return Response(wallet_info, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": exception}, status=status.HTTP_400_BAD_REQUEST)


class WalletAPIView(generics.ListCreateAPIView):
    serializer_class = WalletSerializer

    def get_queryset(self):
        current_user = self.request.user
        wallet = Wallet.objects.filter(owner=current_user)
        return wallet
