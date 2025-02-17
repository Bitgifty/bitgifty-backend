from django.http import Http404
# from django.shortcuts import render
from rest_framework import generics, permissions
from . import models, serializers

# Create your views here.


class PointsAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny,]
    serializer_class = serializers.PointSerializer

    def get_queryset(self):
        return models.Point.objects.all().order_by('-point')


class PointsDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny,]
    serializer_class = serializers.PointSerializer
    lookup_field = "wallet_address"

    def get_object(self):
        queryset = self.get_queryset()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {
            f"{self.lookup_field}__iexact": self.kwargs[lookup_url_kwarg]
        }

        obj = queryset.filter(**filter_kwargs).first()
        if obj is None:
            raise Http404("Points not found")
        return obj

    def get_queryset(self):
        return models.Point.objects.all()
