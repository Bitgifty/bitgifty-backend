from django.shortcuts import render

from rest_framework import generics

from .permissions import PayoutPermissions
from .serializers import PayoutSerializer
from .models import Payout
# Create your views here.


class PayoutListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PayoutSerializer
    def get_queryset(self):
        payout = Payout.objects.filter(user=self.request.user)
        return payout


class PayoutDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PayoutSerializer
    queryset = Payout.objects.all()
    permission_classes = (PayoutPermissions, )
    
