"""
Customized user permissions
"""
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and
                    request.user.user_type == 'admin')


class IsHomeSeeker(permissions.BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and
                    request.user.user_type == 'home_seeker')


class IsPropertyOwner(permissions.BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and
                    request.user.user_type == 'property_owner')
