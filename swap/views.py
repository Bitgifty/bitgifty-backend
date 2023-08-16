import math

from django.shortcuts import render

from rest_framework import generics, response, views, exceptions

from .serializers import SwapSerializer
from .models import Swap, SwapTable
from core.utils import get_rate, get_naira_price

# Create your views here.



class SwapAPIView(generics.ListCreateAPIView):
    serializer_class = SwapSerializer
    queryset = Swap.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = Swap.objects.filter(swap_from__owner=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)


class SwapRateAPIView(views.APIView):
    def get(self, request, using):
        try:
            usd_price = get_rate(using)
            naira_rate = get_naira_price()
            rate = math.floor(naira_rate * usd_price)
        except SwapTable.DoesNotExist:
            raise exceptions.ValidationError("Swap not supported")
        return response.Response(rate)


class GetUSDTAPIView(views.APIView):
    def get(self, request, using):
        try:
            usd_price = get_rate(using)
        except SwapTable.DoesNotExist:
            raise exceptions.ValidationError("Not found")
        return response.Response(usd_price)
        