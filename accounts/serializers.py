from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from django.contrib.auth import get_user_model, authenticate
User = get_user_model()


class CustomRegistrationSerializer(RegisterSerializer):
    pass


class CustomUserDetailSerializer(UserDetailsSerializer):
    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'email', 'phone_number')
        read_only_fields = ('email', )
