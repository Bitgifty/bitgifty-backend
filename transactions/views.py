import requests

from django.shortcuts import render
from django.http import Http404

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.serializers import ValidationError
from rest_framework.schemas import SchemaGenerator

from .serializers import TransactionSerializer
from .models import Transaction

from core.utils import Blockchain
from drf_yasg.renderers import OpenAPIRenderer, SwaggerUIRenderer

# Create your views here.


class TransactionListAPIView(generics.GenericAPIView):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    renderer_classes = [OpenAPIRenderer, SwaggerUIRenderer ]

    def get(self, request, pk):
        """Confirms if a payment is legit"""
        user = request.user
        wallet_address = user.wallet_address

        client = Blockchain()
        transactions = client.get_transactions(wallet_address, "tron")

        try:
            return Response(transactions, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": exception}, status=status.HTTP_400_BAD_REQUEST)

