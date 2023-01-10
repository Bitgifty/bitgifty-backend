from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from django.contrib.auth import get_user_model, authenticate
User = get_user_model()


class CustomRegistrationSerializer(RegisterSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    country = serializers.CharField()
    referral_code = serializers.CharField(required=False)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get("password1")

        if password.isdigit():
            raise serializers.ValidationError(
                {'error': 'Password is entirely numeric'})

        if len(password) < 8:
            raise serializers.ValidationError({'error': 'Password too short'})

        if username:
            if User.objects.filter(username=username).exists():
                msg = {'error': 'User aleady exists'}
                raise serializers.ValidationError(msg)
            else:
                return attrs
        else:
            raise serializers.ValidationError({'error': "No username inputed"})
        

    def custom_signup(self, request, user):
        # general
        user.username = self.validated_data.get('username', '')
        user.email = self.validated_data.get('email', '')
        user.phone_number = self.validated_data.get('phone_number', '')
        user.country = self.validated_data.get('country', '')
        user.referral_code = self.validated_data.get('referral_code', '')

        user.save(update_fields=[
            "username",
            "email",
            "phone_number",
            "country",
            "referral_code",
        ])

    class Meta:
        ref_name = "CustomLoginSerializer"


class CustomUserDetailSerializer(UserDetailsSerializer):
    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'email', 'phone_number')
        read_only_fields = ('email', )
