"""
Tests for models.
"""
import pytest
from django.contrib.auth import get_user_model
from user.user_factory import UserFactory

User = get_user_model()


@pytest.mark.django_db
def test_user_factory():
    """Test creating a user with an email is successful."""
    user = UserFactory()

    assert User.objects.filter(email=user.email).exists()


@pytest.mark.django_db
def test_create_user_with_email_successful():
    """Test creating a user with an email is successful."""
    email = 'test@example.com'
    password = 'testpass123'

    user = User.objects.create_user(email=email, password=password)

    user_qr = User.objects.get(email=user.email)
    assert user_qr.email == email
    assert user_qr.check_password(password) is True


@pytest.mark.django_db
def test_new_user_email_normalized():
    """Test email is normalized for new users."""
    sample_emails = [
        ['test1@EXAMPLE.com', 'test1@example.com'],
        ['Test2@Example.com', 'Test2@example.com'],
        ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
        ['test4@example.COM', 'test4@example.com'],
    ]

    for email, expected in sample_emails:
        user = User.objects.create_user(email, 'sample123')
        # self.assertEqual(user.email, expected)
        # user = UserFactory(email=email)
        assert user.email == expected


@pytest.mark.django_db
def test_new_user_without_email_raises_error():
    """Test that creating a user without an email raises a ValueError."""
    with pytest.raises(ValueError):
        User.objects.create_user('', 'test123')


@pytest.mark.django_db
def test_create_user_with_valid_data():
    user = User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        gender='M',
        user_type='home_seeker'
    )
    assert user.email == 'test@example.com'
    assert user.gender == 'M'
    assert user.user_type == 'home_seeker'
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser


@pytest.mark.django_db
def test_create_user_with_invalid_gender():
    with pytest.raises(ValueError):
        User.objects.create_user(
            email='invalidgender@example.com',
            password='testpass123',
            gender='Invalid',
            user_type='home_seeker'
        )


@pytest.mark.django_db
def test_create_user_with_invalid_usertype():
    with pytest.raises(ValueError):
        User.objects.create_user(
            email='invalidusertype@example.com',
            password='testpass123',
            gender='M',
            user_type='Invalid'
        )


@pytest.mark.django_db
def test_create_superuser():
    """Test creating a superuser."""
    user = User.objects.create_superuser(
        'test@exmple.com',
        'test123',
    )
    assert user.is_superuser is True
    assert user.is_staff is True
