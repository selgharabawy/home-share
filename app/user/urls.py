"""
URL mappings for the user API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from user import views

app_name = 'user'

router = DefaultRouter()
router.register(r'users', views.UserView, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('token/',
         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/',
         TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/',
         views.LogoutView.as_view(), name='auth_logout'),
]
