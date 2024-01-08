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

CREATE_LIST_USERS_URL = reverse('user:user-list')
ACCESS_TOKEN_URL = reverse('user:token_obtain_pair')
REFRESH_TOKEN_URL = reverse('user:token_refresh')
LOGOUT_URL = reverse('user:auth_logout')
ME_URL = reverse('user:me')


@pytest.fixture
def admin(db):
    return UserFactory(user_type='admin')


@pytest.fixture
def client(admin):
    client = APIClient()
    client.force_authenticate(admin)
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


@pytest.fixture
def superuser():
    return User.objects.create_superuser(
        email='superuser@example.com',
        name='superuser',
        is_active=True,
        gender='M',
        user_type='admin'
    )


@pytest.fixture
def superuser_client(superuser):
    client = APIClient()
    client.force_authenticate(user=superuser)
    return client


@pytest.fixture
def adminuser():
    return User.objects.create_user(
        email='admin@example.com',
        name='admin',
        is_active=True,
        gender='M',
        user_type='admin'
    )


@pytest.fixture
def admin_client(adminuser):
    client = APIClient()
    client.force_authenticate(user=adminuser)
    return client


@pytest.mark.django_db
def test_retrieve_profile_success(client, admin):
    """Test retrieving profile for logged in user."""
    res = client.get(ME_URL)

    assert res.status_code == status.HTTP_200_OK
    assert res.data == {
        'name': admin.name,
        'email': admin.email,
        'gender': admin.gender,
        'user_type': admin.user_type,
        'is_active': admin.is_active,
    }


@pytest.mark.django_db
def test_post_me_not_allowed(client):
    """Test POST is not allowed for the ME endpoint."""
    res = client.post(ME_URL, {})

    assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_update_user_profile(client, admin):
    """Test updating the user profile for the authenticated user."""
    payload = {
        'name': "Updated name", 'password': 'newpassword123'
    }

    res = client.patch(ME_URL, payload)

    admin.refresh_from_db()
    assert admin.name == payload['name']
    assert admin.check_password(payload['password']) is True
    assert res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_successful_list_users_successful_for_admin_users(client):
    """Test list users for the authenticated admin user is successful."""
    for i in range(0, 5):
        UserFactory(user_type='home_seeker')
        UserFactory(user_type='property_owner')
    res = client.get(CREATE_LIST_USERS_URL)

    assert res.status_code == status.HTTP_200_OK
    assert len(res.data) == 10


@pytest.mark.django_db
def test_no_admin_users_returned_in_list_users(client):
    """Test list users for the authenticated admin user is successful."""
    for i in range(0, 5):
        UserFactory(user_type='home_seeker')
        UserFactory(user_type='property_owner')
        UserFactory(user_type='admin')
    res = client.get(CREATE_LIST_USERS_URL)

    assert res.status_code == status.HTTP_200_OK
    assert len(res.data) == 10


@pytest.mark.django_db
def test_superusers_list_users_including_admins(superuser_client):
    """Test list users for the superuser includes admin users is successful."""
    for i in range(0, 5):
        UserFactory(user_type='home_seeker')
        UserFactory(user_type='property_owner')
        UserFactory(user_type='admin')
    res = superuser_client.get(CREATE_LIST_USERS_URL)

    assert res.status_code == status.HTTP_200_OK
    assert len(res.data) == 16


@pytest.mark.django_db
def test_superusers_can_create_admin_user(superuser_client):
    """Test superuser can create admin users is successful."""
    payload = {
        "email": "admin_new@example.com",
        "password": "admin_pass",
        "name": "admin",
        "gender": "M",
        "user_type": "admin",
        "is_active": True
    }

    res = superuser_client.post(CREATE_LIST_USERS_URL, payload)

    assert res.status_code == status.HTTP_201_CREATED
    user = User.objects.get(email=payload['email'])
    assert user.check_password(payload['password']) is True


@pytest.mark.django_db
def test_admin_cannot_create_admin_user(admin_client):
    """Test superuser can create admin users is successful."""
    payload = {
        "email": "admin_new@example.com",
        "password": "admin_pass",
        "name": "admin",
        "gender": "M",
        "user_type": "admin",
        "is_active": True
    }

    res = admin_client.post(CREATE_LIST_USERS_URL, payload)

    assert res.status_code == status.HTTP_403_FORBIDDEN
    assert User.objects.filter(email=payload['email']).exists() is False


@pytest.mark.django_db
def test_home_seekers_cannot_list_users():
    """Test authenticated home seekers are forbidden to list users."""
    user = UserFactory(user_type='home_seeker')
    client = APIClient()
    client.force_authenticate(user=user)
    for i in range(0, 5):
        UserFactory(user_type='home_seeker')
        UserFactory(user_type='property_owner')
        UserFactory(user_type='admin')
    res = client.get(CREATE_LIST_USERS_URL)

    assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_property_owners_cannot_list_users():
    """Test authenticated property owners are forbidden to list users."""
    user = UserFactory(user_type='property_owner')
    client = APIClient()
    client.force_authenticate(user=user)
    for i in range(0, 5):
        UserFactory(user_type='home_seeker')
        UserFactory(user_type='property_owner')
        UserFactory(user_type='admin')
    res = client.get(CREATE_LIST_USERS_URL)

    assert res.status_code == status.HTTP_403_FORBIDDEN


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
