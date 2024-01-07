"""
Tests for the user public API.
"""
import pytest
from django.contrib.auth import get_user_model
from user.user_factory import UserFactory

from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

CREATE_USER_URL = reverse('user:create')
ACCESS_TOKEN_URL = reverse('user:token_obtain_pair')
REFRESH_TOKEN_URL = reverse('user:token_refresh')
ME_URL = reverse('user:me')


@pytest.fixture
def client():
    client = APIClient()
    return client


@pytest.fixture
def user_details():
    user_details = {
        'name': 'Test Name',
        'email': 'test@example.com',
        'password': 'test-user-password123'
    }
    User.objects.create_user(**user_details)
    return user_details


@pytest.mark.django_db
def test_create_user_success(client):
    """Test creating a user with an email is successful."""
    payload = {
        'email': 'test@example.com',
        'password': 'testpass123',
        'name': 'Test Name',
        'user_type': 'home_seeker',
        'gender': 'M'
    }
    res = client.post(CREATE_USER_URL, payload)

    assert res.status_code == status.HTTP_201_CREATED
    user = User.objects.get(email=payload['email'])
    assert user.check_password(payload['password']) is True
    assert 'password' not in res.data


@pytest.mark.django_db
def test_user_with_email_exists_error(client):
    """Test error returned if user with email exists."""
    payload = {
        'email': 'test@example.com',
        'password': 'testpass123',
        'name': 'Test Name',
    }
    UserFactory(**payload)
    res = client.post(CREATE_USER_URL, payload)

    assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_password_too_short_error(client):
    """Test an error is returned if password less than 5 chars."""
    payload = {
        'email': 'test@example.com',
        'password': 'test',
        'name': 'Test Name',
    }
    res = client.post(CREATE_USER_URL, payload)

    assert res.status_code == status.HTTP_400_BAD_REQUEST
    user_exists = get_user_model().objects.filter(
        email=payload['email']
    ).exists()
    assert user_exists is False


@pytest.mark.django_db
def test_create_access_token_for_user(client, user_details):
    """Test generate token for valid credentials."""
    payload = {
        'email': user_details['email'],
        'password': user_details['password'],
    }
    res = client.post(ACCESS_TOKEN_URL, payload)

    assert 'access' in res.data
    assert 'refresh' in res.data
    assert res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_access_token_bad_credentials(client, user_details):
    """Test returns an error when credentials are invalid."""
    payload = {
        'email': user_details['email'],
        'password': 'wrong-password123',
    }
    res = client.post(ACCESS_TOKEN_URL, payload)

    assert 'access' not in res.data
    assert 'refresh' not in res.data
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_token_blank_password(client, user_details):
    """Test posting blank password returns an error."""
    payload = {
        'email': user_details['email'],
        'password': '',
    }
    res = client.post(ACCESS_TOKEN_URL, payload)

    assert 'access' not in res.data
    assert 'refresh' not in res.data
    assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_refresh_access_token(client, user_details):
    """Test refreshing access token with refresh token."""
    payload = {
        'email': user_details['email'],
        'password': user_details['password'],
    }
    # Obtain the access and refresh tokens
    response = client.post(ACCESS_TOKEN_URL, payload)
    refresh_token = response.data['refresh']

    # Use refresh token to obtain new access token
    refresh_payload = {'refresh': refresh_token}
    refresh_response = client.post(REFRESH_TOKEN_URL, refresh_payload)

    assert refresh_response.status_code == status.HTTP_200_OK
    assert 'access' in refresh_response.data


@pytest.mark.django_db
def test_retrieve_user_unauthorized(client):
    """Test authentication is required for users."""
    res = client.get(ME_URL)

    assert res.status_code == status.HTTP_401_UNAUTHORIZED
