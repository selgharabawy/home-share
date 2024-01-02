"""
Tests for the Django admin modifications.
"""
import pytest
from django.urls import reverse
from django.test import Client
from user.user_factory import UserFactory
from django.contrib.auth import get_user_model


@pytest.fixture
def admin_user(db):
    return get_user_model().objects.create_superuser(
        email='admin@example.com', password='testpass123')


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def client(admin_user):
    client = Client()
    client.force_login(admin_user)
    return client


def test_users_list(client, user):
    """Test that users are listed on page."""
    url = reverse('admin:user_user_changelist')
    res = client.get(url)

    assert user.name in res.content.decode()
    assert user.email in res.content.decode()


def test_edit_user_page(client, user):
    """Test the edit user page works"""
    url = reverse('admin:user_user_change', args=[user.id])
    res = client.get(url)

    assert res.status_code == 200


def test_create_user_page(client):
    """Test the create user page works."""
    url = reverse('admin:user_user_add')
    res = client.get(url)

    assert res.status_code == 200
