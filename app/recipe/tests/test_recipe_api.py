from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe import serializers


RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """ create and return a recipe obj """
    default_val = {
        'title': 'test recipe title',
        'time_minutes': 10,
        'price': 5.00
    }
    default_val.update(params)

    return Recipe.objects.create(user=user, **default_val)


class PublicRecipeAPITest(TestCase):
    """ Test unauthorized recipe api"""

    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        """ test that authentication required for get list of recipes."""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """ Test authorized recipe api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@testmail.com",
            password='testPass'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_list_successful(self):
        """ test that retrieve recipe list work successful."""
        sample_recipe(self.user)
        sample_recipe(self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = serializers.RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_limited_to_user(self):
        """ test that list return authorized user recipes."""
        user2 = get_user_model().objects.create_user(
            email="test2@testmail.com",
            password='testPass'
        )
        sample_recipe(user2)
        sample_recipe(self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = serializers.RecipeSerializer(recipes, many=True)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
