"""
Database User models.
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(
            self, email, password=None,
            gender='M', user_type='admin',
            **extra_fields
    ):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        if gender not in ['M', 'F']:
            raise ValueError('Gender must be Male or Female.')
        if user_type not in [
            'home_seeker',
            'property_owner',
            'admin'
        ]:
            raise ValueError(
                'User Type must be Administrator, \
                Home Seeker or Property Owner.'
            )
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.is_staff = True if user_type == 'admin' else False
        user.set_password(password)
        user.gender = gender
        user.user_type = user_type
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default='M'
    )

    USER_TYPE_CHOICES = [
        ('home_seeker', 'Home Seeker'),
        ('property_owner', 'Property Owner'),
        ('admin', 'Administrator'),
    ]
    user_type = models.CharField(
        max_length=14,
        choices=USER_TYPE_CHOICES,
        default='admin'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
