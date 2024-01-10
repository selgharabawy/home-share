"""
Views for the API.
"""
from rest_framework import generics, mixins, viewsets, status, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken, OutstandingToken
)
from .permissions import IsAdminUser, IsSuperUser

from user.serializers import (
    UserSerializer,
    SuperUserSerializer,
    UserImageSerializer,
    LogoutSerializer
)
from django.contrib.auth import get_user_model

User = get_user_model()


class UserView(
            mixins.ListModelMixin,
            mixins.CreateModelMixin,
            viewsets.GenericViewSet
):
    """Create a new user in the system."""
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:  # For list action and any other actions
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            if IsSuperUser().has_permission(self.request, self):
                # If the user is a superuser, return all users
                return User.objects.all()
        # Filter out admin users
        return User.objects.exclude(user_type='admin')

    def get_serializer_class(self):
        if (
            self.action == 'list' and
            IsSuperUser().has_permission(self.request, self)
        ):
            return SuperUserSerializer
        elif self.action == 'upload_image':
            return UserImageSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        user_type = request.data.get('user_type')
        if (
            user_type == 'admin' and
            not IsSuperUser().has_permission(request, self)
        ):
            # Deny create an admin user for non-superuser
            return Response(
                {
                    'detail':
                    'Only superusers can create admin users.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Proceed with the standard creation process
        return super().create(request, *args, **kwargs)

    @action(
        methods=['POST'],
        detail=True,
        url_path='upload-image',
        url_name='upload-image'
    )
    def upload_image(self, request, pk=None):
        """Upload an image to user."""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            # blacklist all outstanding tokens for the user
            for token in OutstandingToken.objects.filter(user=request.user):
                BlacklistedToken.objects.get_or_create(token=token)

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticatd user."""
        return self.request.user


class ManageUserImageView(generics.UpdateAPIView):
    """Update Image the authenticated user."""
    serializer_class = UserImageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']

    def get_object(self):
        """Retrieve and return the authenticatd user."""
        return self.request.user
