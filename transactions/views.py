import os


from django.shortcuts import render
from django.http import Http404

from rest_framework import generics
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.exceptions import ParseError as ValidationError


from . import serializers
from .models import Transaction

from core.utils import Blockchain
from wallets.models import Wallet
from drf_yasg.renderers import OpenAPIRenderer, SwaggerUIRenderer
from drf_yasg.utils import swagger_auto_schema

# Create your views here.


class FiatTransactionListAPIView(generics.ListAPIView):
    serializer_class = serializers.TransactionSerializer
    def get_queryset(self):
        query = Transaction.objects.filter(user=self.request.user)
        return query


class TransactionListAPIView(generics.GenericAPIView):
    serializer_class = serializers.TransactionSerializer
    queryset = Transaction.objects.all()
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, OpenAPIRenderer, SwaggerUIRenderer]

    @swagger_auto_schema(query_serializer=serializers.TransactionSerializer)
    def get(self, request, network):
        """Confirms if a payment is legit"""
        # try:
        user = request.user
        wallet_dict = {}
        client = Blockchain(os.getenv("TATUM_API_KEY"), os.getenv("BIN_KEY"), os.getenv("BIN_SECRET"))
        
        if network == "all":
            wallets = Wallet.objects.filter(owner=user)
            for wallet in wallets:
                wallet_dict[wallet.network.lower()] = wallet.address
            transactions = client.get_transactions(wallet_dict, network)
        if network == "naira":
            transactions = Transaction.objects.filter(user=request.user)
        else:
            wallet = Wallet.objects.get(owner=user, network=network.title()) 
            wallet_dict[wallet.network.lower()] = wallet.address
            transactions = client.get_transactions(wallet_dict, network)

        return Response(transactions)
        # except Exception as exception:
        #     raise ValidationError({"error": str(exception)})


class WithdrawAPIView(generics.GenericAPIView):
    serializer_class = serializers.WithdrawalSerializer
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, OpenAPIRenderer, SwaggerUIRenderer]

    @swagger_auto_schema(request_body=serializers.WithdrawalSerializer)
    def post(self, request):
        serializer = serializers.WithdrawalSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            receiver_address = serializer.validated_data.get("receiver_address")
            account_number = serializer.validated_data.get("account_number")
            transaction_type = serializer.validated_data.get("transaction_type")
            amount = serializer.validated_data.get("amount")
            network = serializer.validated_data.get("network")
            client = Blockchain(os.getenv("TATUM_API_KEY"), os.getenv("BIN_KEY"), os.getenv("BIN_SECRET"))
            
            try:
                wallet = Wallet.objects.get(owner=user, network=network)
            except Wallet.DoesNotExist:
                raise ValidationError("Sender wallet not found")

            if network == "naira" or transaction_type == "fiat":
                try:
                    wallet.deduct(float(amount))
                    Transaction.objects.create(
                        user=user,
                        amount=amount,
                        status="pending"
                    )
                    wallet.notify_withdraw_handler(float(amount), account_number)

                    return Response("success")
                except Exception as exception:
                    raise ValidationError(exception)
            else:
                private_key = wallet.private_key
                mnemonic = client.decrypt_crendentails(private_key)
                try:
                    response = client.send_token(receiver_address, network.lower(), str(amount), mnemonic, wallet.address)
                except Exception as exception:
                    raise ValidationError(str(exception))
                if response.get("txId"):
                    return Response(response)
                else:
                    raise ValidationError(response)
        else:
            raise ValidationError({"error": "something went wrong"})
