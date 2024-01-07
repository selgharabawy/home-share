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
LOGOUT_URL = reverse('user:auth_logout')
ME_URL = reverse('user:me')


@pytest.fixture
def home_seeker(db):
    return UserFactory(user_type='home_seeker')


@pytest.fixture
def client(home_seeker):
    client = APIClient()
    client.force_authenticate(home_seeker)
    return client


@pytest.fixture
def user_details_authenticated():
    user_details = {
        'name': 'Test Name',
        'email': 'test@example.com',
        'password': 'test-user-password123'
    }
    User.objects.create_user(**user_details)
    client = APIClient()
    res = client.post(ACCESS_TOKEN_URL, {
        'email': user_details['email'],
        'password': user_details['password']
    })
    user_details['refresh'] = res.data['refresh']
    return user_details


@pytest.fixture
def refresh_client(user_details_authenticated):
    user = User.objects.get(email=user_details_authenticated['email'])
    refresh_client = APIClient()
    refresh_client.force_authenticate(user=user)
    return refresh_client


@pytest.mark.django_db
def test_retrieve_profile_success(client, home_seeker):
    """Test retrieving profile for logged in user."""
    res = client.get(ME_URL)

    assert res.status_code == status.HTTP_200_OK
    assert res.data == {
        'name': home_seeker.name,
        'email': home_seeker.email,
        'gender': home_seeker.gender,
        'user_type': home_seeker.user_type,
    }


@pytest.mark.django_db
def test_post_me_not_allowed(client):
    """Test POST is not allowed for the ME endpoint."""
    res = client.post(ME_URL, {})

    assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_update_user_profile(client, home_seeker):
    """Test updating the user profile for the authenticated user."""
    payload = {
        'name': "Updated name", 'password': 'newpassword123'
    }

    res = client.patch(ME_URL, payload)

    home_seeker.refresh_from_db()
    assert home_seeker.name == payload['name']
    assert home_seeker.check_password(payload['password']) is True
    assert res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_logout(user_details_authenticated, refresh_client):
    """Test logging out invalidates the token."""
    refresh_token = user_details_authenticated['refresh']
    refresh_payload = {'refresh': refresh_token}

    # Obtain the access and refresh tokens by refresh_token
    token_response = refresh_client.post(
        REFRESH_TOKEN_URL, refresh_payload)

    assert 'access' in token_response.data

    # Perform logout
    logout_response = refresh_client.post(
        LOGOUT_URL, refresh_payload)
    assert logout_response.status_code == status.HTTP_205_RESET_CONTENT

    # Attempt to use the blacklisted refresh token to get a new access token
    new_token_response = refresh_client.post(
        REFRESH_TOKEN_URL, refresh_payload)
    assert new_token_response.status_code == status.HTTP_401_UNAUTHORIZED
