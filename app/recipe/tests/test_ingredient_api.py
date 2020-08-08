from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe import serializers


INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientsAPITest(TestCase):
    """ test the public ingredients api"""

    def setUp(self):
        self.client = APIClient()

    def test_tag_list_unauthorized(self):
        """ test that not return any ingredients when unauthorized."""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITest(TestCase):
    """ test the private ingredients api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@testmail.com',
            'testPassword'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """ test that  retrieve ingredients successful. """
        Ingredient.objects.create(user=self.user, name='name1')
        Ingredient.objects.create(user=self.user, name='name2')
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = serializers.IngredientSerializer(ingredients, many=True)
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """ test that ingredients returned for authenticated user. """
        user2 = get_user_model().objects.create_user(
            'test2@testmail.com',
            'testPass'
        )
        Ingredient.objects.create(user=user2, name='name1')
        ingredient = Ingredient.objects.create(user=self.user, name='name2')
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredients_successful(self):
        """ test that ingredients create successful."""
        payload = {'name': 'testName'}
        res = self.client.post(INGREDIENT_URL, payload)
        ingredient_exist = Ingredient.objects.all().filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ingredient_exist)

    def test_create_ingredients_invalid(self):
        """ test that dont create a invalid ingredient."""
        payload = {'name': ''}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
