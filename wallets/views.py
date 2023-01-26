import os

from django.shortcuts import render

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from .serializers import WalletSerializer
from .models import Wallet

from core.utils import Blockchain
# Create your views here.


class WalletAPIView(generics.GenericAPIView):
    serializer_class = WalletSerializer
    
    def get_queryset(self):
        current_user = self.request.user
        wallet = Wallet.objects.filter(owner=current_user)
        return wallet

    def get(self, request):
        wallet_list = []
        try:
            network_mapping = {
                "bnb": "bsc",
                "bitcoin": "bitcoin",
                "celo": "celo",
                "ethereum": "ethereum",
                "tron": "tron"
            }
            user = request.user
            wallets = Wallet.objects.filter(owner=user)

            for wallet in wallets:
                network_key = wallet.network.lower()
                network = network_mapping[network_key]
                client = Blockchain(os.getenv("TATUM_API_KEY"), os.getenv("BIN_KEY"), os.getenv("BIN_SECRET"))
                wallet_info = client.get_wallet_info(wallet.address, network)
                
                wallet_list.append({
                    'address': wallet.address,
                    'info': wallet_info
                })
            return Response(wallet_list, status=status.HTTP_200_OK)
        except Exception as exception:
            raise ValidationError({"error": exception})
