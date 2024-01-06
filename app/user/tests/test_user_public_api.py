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


@pytest.fixture
def client(admin_user):
    client = APIClient()
    return client


@pytest.mark.django_db
def test_create_user_success(client):
    """Test creating a user with an email is successful."""
    user = UserFactory(user_type='home_seeker')
    # home_seeker_user = UserFactory(user_type='home_seeker')

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
