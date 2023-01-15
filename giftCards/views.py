from django.shortcuts import render

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .serializers import GiftCardSerializer
from .models import GiftCard
# Create your views here.


class GiftCardAPIView(ListCreateAPIView):
    serializer_class = GiftCardSerializer
    queryset = GiftCard.objects.all()

    def perform_create(self, serializer, **kwargs):
        current_user = self.request.user
        kwargs['account'] = current_user
        serializer.save(**kwargs)


class GiftCardDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = GiftCardSerializer
    queryset = GiftCard.objects.all()
