import os


from django.shortcuts import render
from django.http import Http404

from rest_framework import generics
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


from . import serializers
from .models import Transaction

from core.utils import Blockchain
from wallets.models import Wallet
from drf_yasg.renderers import OpenAPIRenderer, SwaggerUIRenderer

from core.utils import env_init
# Create your views here.

env = env_init()

class TransactionListAPIView(generics.GenericAPIView):
    serializer_class = serializers.TransactionSerializer
    queryset = Transaction.objects.all()
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, OpenAPIRenderer, SwaggerUIRenderer]

    def get(self, request, network):
        """Confirms if a payment is legit"""
        # try:
        user = request.user
        wallet_dict = {}
        client = Blockchain(env("TATUM_API_KEY"), env("BIN_KEY"), env("BIN_SECRET"))
        
        if network == "all":
            wallets = Wallet.objects.filter(owner=user)
            for wallet in wallets:
                wallet_dict[wallet.network.lower()] = wallet.address
            transactions = client.get_transactions(wallet_dict, network)
        else:
            wallet = Wallet.objects.get(owner=user, network=network.title()) 
            wallet_dict[wallet.network.lower()] = wallet.address
            transactions = client.get_transactions(wallet_dict, network)

        return Response(transactions)
        # except Exception as exception:
        #     raise ValidationError({"error": str(exception)})


class WithdrawAPIView(generics.GenericAPIView):
    serializer_class = serializers.WithdrawalSerializer
    renderer_classes = [OpenAPIRenderer, SwaggerUIRenderer]

    def post(self, request):
        serializer = serializers.WithdrawalSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            receiver_address = serializer.validated_data.get("receiver_address")
            amount = serializer.validated_data.get("amount")
            network = serializer.validated_data.get("network")
            client = Blockchain(env("TATUM_API_KEY"), env("BIN_KEY"), env("BIN_SECRET"))
            
            try:
                wallet = Wallet.objects.get(owner=user, network=network)
            except Exception:
                raise ValidationError({"error": "Sender wallet not found"})
            private_key = wallet.private_key
            mnemonic = client.decrypt_crendentails(private_key)
            response = client.send_token(receiver_address, network.lower(), str(amount), mnemonic, wallet.address)
            if response.get("txId"):
                return Response(response)
            else:
                raise ValidationError(response)
        else:
            raise ValidationError({"error": "something went wrong"})
