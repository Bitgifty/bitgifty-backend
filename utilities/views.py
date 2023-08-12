import math
from django.shortcuts import render


from rest_framework import generics, exceptions, response

from rest_framework import views

from core.utils import get_naira_price, get_rate

from . import serializers, models

# Create your views here.


class SwapRateAPIView(views.APIView):
    def get(self, request, using):
        try:
            usd_price = get_rate(using)
            tron = 1/usd_price

            naira_rate = get_naira_price()
            naira = 1/naira_rate

            rate = round(naira * tron, 3)
        except Exception:
            raise exceptions.ValidationError("Error converting naira to crypto")
        return response.Response(rate)

class BuyAirtimeAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.BuyAirtimeSerializer
    
    def get_queryset(self):
        user = self.request.user
        query = models.AirtimePurchase.objects.filter(user=user)
        return query
    
    def perform_create(self, serializer, **kwargs):
        user = self.request.user
        kwargs["user"] = user
        try:
            serializer.save(**kwargs)
        except Exception as exception:
            raise exceptions.ValidationError(exception)


class BuyDataAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.BuyDataSerializer

    def get_queryset(self):
        user = self.request.user
        query = models.DataPurchase.objects.filter(user=user)
        return query
    
    def perform_create(self, serializer, **kwargs):
        user = self.request.user
        kwargs["user"] = user
        try:
            serializer.save(**kwargs)
        except Exception as exception:
            raise exceptions.ValidationError(exception)


class BuyCableAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.BuyCableSerializer

    def get_queryset(self):
        query = models.CablePurchase.objects.filter(user=self.request.user)
        return query
    
    def perform_create(self, serializer, **kwargs):
        user = self.request.user
        kwargs["user"] = user
        try:
            serializer.save(**kwargs)
        except Exception as exception:
            raise exceptions.ValidationError(exception)


class BuyElectricityAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.BuyElectricitySerializer

    def get_queryset(self):
        query = models.ElectricityPurchase.objects.filter(user=self.request.user)
        return query
    
    def perform_create(self, serializer, **kwargs):
        user = self.request.user
        kwargs["user"] = user
        try:
            serializer.save(**kwargs)
        except Exception as exception:
            raise exceptions.ValidationError(exception)



class CableAPIView(generics.ListAPIView):
    serializer_class = serializers.CableSerializer
    queryset = models.Cable.objects.all()


class CablePlanAPIView(generics.ListAPIView):
    serializer_class = serializers.CablePlanSerializer
    queryset = models.CablePlan.objects.all()


class NetworkAPIView(generics.ListAPIView):
    serializer_class = serializers.NetworkSerializer
    queryset = models.Network.objects.all()


class DataPlanAPIView(generics.ListAPIView):
    serializer_class = serializers.DataPlanSerializer
    queryset = models.DataPlan.objects.all()


class DiscoAPIView(generics.ListAPIView):
    serializer_class = serializers.DiscoSerializer
    queryset = models.Disco.objects.all()

