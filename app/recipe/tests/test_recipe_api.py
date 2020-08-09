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

    def test_create_recipe_basic(self):
        """ test creating a basic recipe without tags or ingredients."""
        payload = {
            'title': 'test recipe title',
            'time_minutes': 30,
            'price': 5.00
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """ test creating a  recipe with tags."""
        tag1 = sample_tag(self.user)
        tag2 = sample_tag(self.user)
        payload = {
            'title': 'test recipe title',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 30,
            'price': 5.00
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(len(tags), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """ test creating a  recipe with ingredients."""
        ingredient1 = sample_ingredient(self.user)
        ingredient2 = sample_ingredient(self.user)
        payload = {
            'title': 'test recipe title',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 30,
            'price': 5.00
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(len(ingredients), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_create_recipe(self):
        """ test creating a  recipe with ingredients and tags."""
        tag1 = sample_tag(self.user)
        tag2 = sample_tag(self.user)
        ingredient1 = sample_ingredient(self.user)
        ingredient2 = sample_ingredient(self.user)
        payload = {
            'title': 'test recipe title',
            'ingredients': [ingredient1.id, ingredient2.id],
            'tags': [tag1.id, tag2.id],
            'time_minutes': 30,
            'price': 5.00,
            'link': 'test link'
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        tags = recipe.tags.all()

        self.assertEqual(len(tags), 2)
        self.assertEqual(len(ingredients), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
        for key in payload.keys():
            if key == 'tags' or key == 'ingredients':
                continue
            self.assertEqual(payload[key], getattr(recipe, key))
