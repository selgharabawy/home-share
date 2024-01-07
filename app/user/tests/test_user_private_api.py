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

ME_URL = reverse('user:me')


@pytest.fixture
def home_seeker(db):
    return UserFactory(user_type='home_seeker')


@pytest.fixture
def client(home_seeker):
    client = APIClient()
    client.force_authenticate(home_seeker)
    return client


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
