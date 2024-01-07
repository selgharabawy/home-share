"""
User Factory.
"""
from factory import Faker, Iterator
from user.models import User
import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = Faker('email')
    name = Faker('name')
    gender = Iterator(User.GENDER_CHOICES, getter=lambda c: c[0])
    user_type = Iterator(User.USER_TYPE_CHOICES, getter=lambda c: c[0])

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted if extracted else 'defaultpassword'
        self.set_password(password)
