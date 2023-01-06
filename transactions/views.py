import requests

from django.shortcuts import render
from django.http import Http404

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.serializers import ValidationError
from rest_framework.schemas import SchemaGenerator

from .serializers import TransactionSerializer, TransactionConfirmSerializer
from .models import Transaction
from BinanceGift.settings import TATUM_API_KEY

from drf_yasg.renderers import OpenAPIRenderer, SwaggerUIRenderer

# Create your views here.


class TransactionAPIView(ListCreateAPIView):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()


class TransactionDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()


class TransactionConfirmView(GenericAPIView):
    serializer_class = TransactionConfirmSerializer
    queryset = Transaction.objects.all()
    renderer_classes = [OpenAPIRenderer, SwaggerUIRenderer ]
    
    def get_object(self, pk):
        try:
            return Transaction.objects.get(pk=pk)
        except Transaction.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        """Confirms if a payment is legit"""
        transaction = self.get_object(pk)
        serializer = TransactionConfirmSerializer(transaction, data=request.data)


        if serializer.is_valid(self):
            current_user = request.user
            transaction_hash = serializer.validated_data.get("transaction_hash")
            transaction_chain = serializer.validated_data.get("transaction_chain")
            
            url = f"https://api.tatum.io/v3/{transaction_chain}/transaction/" + transaction_hash
            
            # make request to tatum api
            headers = {"x-api-key": TATUM_API_KEY}
            response = requests.get(url, headers=headers)

            data = response.json()
            print(data)
            if current_user.wallet_address != data.to:
                transaction.status = "cancelled"
                transaction.save()
                raise ValidationError("Sent to wrong address")
            elif data.value != transaction.amount:
                transaction.status = "cancelled"
                transaction.save()
                raise ValidationError("Wrong amount sent")
            else:
                transaction.status = "confirmed"
                transaction.save()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)