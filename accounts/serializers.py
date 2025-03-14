from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework.authtoken.serializers import AuthTokenSerializer
from dj_rest_auth.serializers import UserDetailsSerializer, PasswordResetSerializer
from django.contrib.auth import get_user_model, authenticate
User = get_user_model()


class CustomRegistrationSerializer(RegisterSerializer):
    # username = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    referral_code = serializers.CharField(required=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get("password1")

        if password.isdigit():
            raise serializers.ValidationError(
                {'error': 'Password is entirely numeric'})

        if len(password) < 8:
            raise serializers.ValidationError({'error': 'Password too short'})

        if email:
            if User.objects.filter(email=email).exists():
                msg = {'error': 'User aleady exists'}
                raise serializers.ValidationError(msg)
            else:
                return attrs
        else:
            raise serializers.ValidationError({'error': "No username inputed"})
        

    def custom_signup(self, request, user):
        # general
        user.username = self.validated_data.get('email', '')
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
        fields = ('pk', 'first_name', 'last_name', 'email', 'phone_number',)
        read_only_fields = ('email', 'first_name', 'last_name')


class CustomPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        super().get_email_options()
        return {
            'html_email_template_name': 'registration/custom_reset_confirm.html',
        }


class CustomLoginSerializer(AuthTokenSerializer):
    username = None
    email = serializers.CharField(
        label=("Email"),
        write_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = ('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = ('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
