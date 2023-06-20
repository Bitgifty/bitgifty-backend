from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .serializers import GiftCardSerializer, RedeemSerializer, GiftCardImageSerializer
from .models import GiftCard, Redeem, GiftCardImage
# Create your views here.


class GiftCardAPIView(ListCreateAPIView):
    serializer_class = GiftCardSerializer
    queryset = GiftCard.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = GiftCard.objects.filter(account=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer, **kwargs):
        current_user = self.request.user
        kwargs['account'] = current_user
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
        kwargs['account'] = current_user
        serializer.save(**kwargs)

    def list(self, request, *args, **kwargs):
        queryset = Redeem.objects.filter(account=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
