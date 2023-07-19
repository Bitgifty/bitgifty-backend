from django.shortcuts import render

from rest_framework import generics, response

from .serializers import SwapSerializer
from .models import Swap

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