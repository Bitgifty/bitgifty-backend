from django.shortcuts import render
from django.contrib.auth import login

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator

from knox.views import LoginView as KnoxLogin
from drf_yasg.renderers import SwaggerUIRenderer, OpenAPIRenderer
from drf_yasg.utils import swagger_auto_schema
from .serializers import CustomLoginSerializer

# Create your views here.

class CustomKoxLogin(KnoxLogin):
    serializer_class = CustomLoginSerializer
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(request_body=CustomLoginSerializer)
    def post(self, request, format=None):
        serializer = CustomLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(CustomKoxLogin, self).post(request, format=None)
    
    def get_post_response_data(self, request, token, instance):
        UserSerializer = self.get_user_serializer_class()

        data = {
            'expiry': self.format_expiry_datetime(instance.expiry),
            'key': token
        }
        if UserSerializer is not None:
            data["user"] = UserSerializer(
                request.user,
                context=self.get_context()
            ).data
        return data