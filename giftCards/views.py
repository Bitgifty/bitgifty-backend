from django.shortcuts import render

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .serializers import GiftCardSerializer, RedeemSerializer, GiftCardImageSerializer
from .models import GiftCard, Redeem, GiftCardImage
from wallets.models import Wallet
# Create your views here.


class GiftCardAPIView(ListCreateAPIView):
    serializer_class = GiftCardSerializer
    queryset = GiftCard.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = GiftCard.objects.filter(wallet__owner=request.user).order_by("-id")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer, **kwargs):
        current_user = self.request.user
        network = serializer.validated_data.get("currency")
        wallet = Wallet.objects.get(
            owner=current_user, network=network.title()
        )
        kwargs['wallet'] = wallet
        try:
            kwargs['code'] = wallet.create_giftcard(serializer.validated_data.get("amount"))
        except Exception as exception:
            raise serializers.ValidationError(exception)
        serializer.save(**kwargs)


class GiftCardDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = GiftCardSerializer
    queryset = GiftCard.objects.all()


class GiftCardImageAPIView(ListCreateAPIView):
    serializer_class = GiftCardImageSerializer
    queryset = GiftCardImage.objects.all()


class GiftCardImageDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = GiftCardImageSerializer
    queryset = GiftCardImage.objects.all()


class RedeemAPIView(ListCreateAPIView):
    serializer_class = RedeemSerializer
    queryset = Redeem.objects.all()

    def perform_create(self, serializer, **kwargs):
        current_user = self.request.user
        code = serializer.validated_data.get("code")
        giftcard = GiftCard.objects.get(code=code)
        network = giftcard.currency.lower()
        wallet = Wallet.objects.get(
            owner=current_user, network=network.title()
        )
        kwargs['wallet'] = wallet
        try:
            wallet.redeem_giftcard(code)
        except Exception as exception:
            raise serializers.ValidationError(exception)
        serializer.save(**kwargs)

    def list(self, request, *args, **kwargs):
        queryset = Redeem.objects.filter(wallet__owner=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
