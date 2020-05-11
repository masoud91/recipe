from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """test creating user with valid payload is successful"""
        payload = {
            'email': 'demo@idco.io',
            'password': 'demo1234',
            'name': 'Demo User',
        }

        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_exist(self):
        """Test creating a user that already exists"""
        payload = {
            'email': 'demo@idco.io',
            'password': 'demo1234',
        }

        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password must be more than 5 characters"""
        payload = {
            'email': 'demo@idco.io',
            'password': 'short',
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that token is created for the user"""
        payload = {
            'email': 'demo@idco.io',
            'password': 'demo1234',
        }
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_with_invalid_credential(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(**{
            'email': 'demo@idco.io',
            'password': 'demo1234',
        })

        payload = {
            'email': 'demo@idco.io',
            'password': 'WrongPassword',
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user does not exists"""
        payload = {
            'email': 'demo@idco.io',
            'password': 'demo1234',
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        payload = {
            'email': 'demo',
            'password': '',
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_authorized(self):
        """Test that authentication is required for users"""
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProtectedUserApiTest(TestCase):
    """Test api requests that require authentication"""

    def setUp(self) -> None:
        self.user = create_user(
            email='u1@idco.io',
            password='pass123456',
            name='user one',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in used"""
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({
            'name': self.user.name,
            'email': self.user.email,
        }, response.data)
        self.assertNotIn('password', response.data)

    def test_post_me_not_allowed(self):
        """Test that POST in not allowed on user/me url"""
        response = self.client.post(ME_URL, {})

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {
            'name': 'name edited',
            'password': 'changed',
        }
        response = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
