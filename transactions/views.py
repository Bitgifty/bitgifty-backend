import os


from django.shortcuts import render
from django.http import Http404

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
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
    renderer_classes = [OpenAPIRenderer, SwaggerUIRenderer]

    def get(self, request):
        """Confirms if a payment is legit"""
        try:
            user = request.user
            wallet_address = user.wallet_address

            client = Blockchain(env("TATUM_API_KEY"), env("BIN_KEY"), env("BIN_SECRET"))
            transactions = client.get_transactions(wallet_address, "tron")
            return Response(transactions, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)}, status=status.HTTP_400_BAD_REQUEST)


class WithdrawAPIView(generics.GenericAPIView):
    serializer_class = serializers.WithdrawalSerializer
    renderer_classes = [OpenAPIRenderer, SwaggerUIRenderer]

    def post(self, request):
        serializer = serializers.WithdrawalSerializer(data=request.data)
        try:
            if serializer.is_valid():
                user = request.user
                receiver_address = serializer.validated_data.get("receiver_address")
                amount = serializer.validated_data.get("amount")
                network = serializer.validated_data.get("network")
                client = Blockchain(env("TATUM_API_KEY"), env("BIN_KEY"), env("BIN_SECRET"))
                wallet = Wallet.objects.get(owner=user, network=network)
                private_key = wallet.private_key
                mnemonic = client.decrypt_crendentails(private_key)
                response = client.send_token(receiver_address, network, str(amount), mnemonic, wallet.address)
                if response["txId"]:
                    return Response(response)
                else:
                    raise ValidationError(response)
            else:
                raise ValidationError({"error": "something went wrong"})
        except Exception as exception:
            raise ValidationError({"error": str(exception)})
