from rest_framework import serializers

from . import models


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Point
        fields = "__all__"
