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
from drf_yasg.renderers import OpenAPIRenderer, SwaggerUIRenderer

# Create your views here.


class TransactionListAPIView(generics.GenericAPIView):
    serializer_class = serializers.TransactionSerializer
    queryset = Transaction.objects.all()
    renderer_classes = [OpenAPIRenderer, SwaggerUIRenderer]

    def get(self, request):
        """Confirms if a payment is legit"""
        try:
            user = request.user
            wallet_address = user.wallet_address

            client = Blockchain(os.getenv("TATUM_API_KEY"), os.getenv("BIN_KEY"), os.getenv("BIN_SECRET"))
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
            if serializer.is_valid(self):
                user = request.user
                receiver_address = serializer.validated_data.get("receiver_address")
                amount = serializer.validated_data.get("receiver_address")
                client = Blockchain(os.getenv("TATUM_API_KEY"), os.getenv("BIN_KEY"), os.getenv("BIN_SECRET"))
                if user.wallet_seed:
                    encrypted_mnemonic = user.wallet_seed
                    mnemonic = client.decrypt_crendentails(encrypted_mnemonic)
                    client.send_token(receiver_address, "tron", amount, mnemonic)
                else:
                    ValidationError({"error": "wallet seed not inputted"})
            else:
                raise ValidationError({"error": "something went wrong"})
        except Exception as exception:
            raise ValidationError({"error": str(exception)})
