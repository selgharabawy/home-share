"""
User Factory.
"""
from factory import Faker
from user.models import User
import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = Faker('email')
    name = Faker('name')
