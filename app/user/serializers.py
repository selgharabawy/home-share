"""
Serializers for the user API View
"""
from django.contrib.auth import (
    get_user_model,
    # authenticate,  # token related
)
# from django.utils.translation import gettext as _  # token related

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'password', 'name',
                  'gender', 'user_type', 'is_active', 'image']
        read_only_fields = ['id', 'image']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
            'gender': {'required': True},
            'user_type': {'required': True},
        }

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class UserImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to users."""

    class Meta:
        model = get_user_model()
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}


class SuperUserSerializer(serializers.ModelSerializer):
    """Serializer for the user objects to superuser auth."""
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['is_staff', 'is_superuser']


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
