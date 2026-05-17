from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        required=True,
        style={'input_type': 'password'}
    )

    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password']

        extra_kwargs = {
            'email': {
                'required': True,
                'allow_blank': False,
            }
        }

    def validate(self, attrs):

        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError(
                {"password": _("Passwords do not match")}
            )

        validate_password(password)

        return attrs

    def create(self, validated_data):

        validated_data.pop('confirm_password')

        return User.objects.create_user(**validated_data)


class SignInSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):

        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            username=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError(
                _("Invalid credentials")
            )

        attrs['user'] = user
        return attrs


class SignOutSerializer(serializers.Serializer):

    refresh = serializers.CharField()

    def validate(self, attrs):

        refresh = attrs.get('refresh')

        try:
            token = RefreshToken(refresh)
            token.blacklist()

        except TokenError:
            raise serializers.ValidationError(
                _("Invalid or expired token")
            )

        return attrs
