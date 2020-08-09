from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe import serializers


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """ return recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='test tag name'):
    """ create and return a recipe obj """
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='test ingredient name'):
    """ create and return a recipe obj """
    return Ingredient.objects.create(user=user, name=name)


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

    def test_recipe_detail(self):
        """ test viewing a recipe detail. """
        recipe = sample_recipe(self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = serializers.RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
