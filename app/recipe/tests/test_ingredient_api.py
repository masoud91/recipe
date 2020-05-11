from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient

from recipe.serializer import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngTests(TestCase):
    """Test publicly available APIs for Ingredient"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_check_authentication_is_required(self):
        """Check that API requires authentication"""
        response = self.client.get(INGREDIENT_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProtectedIngTests(TestCase):
    """Test protected APIs for Ingredient"""

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            'demo@idco.io',
            'pass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients(self):
        """Test get ingredient list"""
        Ingredient.objects.create(user=self.user, name='Beef')
        Ingredient.objects.create(user=self.user, name='Chicken')

        response = self.client.get(INGREDIENT_URL)

        ings_query = Ingredient.objects.all().order_by('-name')
        ings_serializer = IngredientSerializer(ings_query, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ings_serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients returned are for the current user """
        another_user = get_user_model().objects.create_user(
            'demo2@idco.io',
            'pass123'
        )
        Ingredient.objects.create(user=another_user, name='Beef')

        payload = {'name': 'Chicken'}
        Ingredient.objects.create(user=self.user, name=payload['name'])

        response = self.client.get(INGREDIENT_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], payload['name'])

    def test_create_ingredient_successful(self):
        """Test creating a new ingredient is successful"""
        payload = {'name': 'steak'}
        response = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        )

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating a new ingredient with invalid payload"""
        payload = {'name': ''}
        response = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
