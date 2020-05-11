from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='demo@idco.io', password='test1234'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating user with email is successful"""
        email = 'masoud@idco.io'
        password = 'pass1234'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for new user is normalized"""
        email = 'masoud@IDCO.IO'
        password = 'pass1234'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raise error"""
        email = None
        password = 'pass1234'

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=email,
                password=password
            )

    def test_create_new_super_user(self):
        """Test creating a new SuperUser"""
        email = 'admin@idco.io'
        password = 'pass1234'
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ing = models.Tag.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ing), ing.name)
