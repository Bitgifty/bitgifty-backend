from django.shortcuts import render

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .serializers import GiftCardSerializer
from .models import GiftCard
# Create your views here.


class GiftCardAPIView(ListCreateAPIView):
    serializer_class = GiftCardSerializer
    queryset = GiftCard.objects.all()


class GiftCardDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = GiftCardSerializer
    queryset = GiftCard.objects.all()
