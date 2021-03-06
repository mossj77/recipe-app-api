import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe import serializers


RECIPE_URL = reverse('recipe:recipe-list')


def upload_image_url(recipe_id):
    """ return upload images of recipe url"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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

    def test_partial_recipe_update(self):
        """ test that some update work(patch)."""
        recipe = sample_recipe(self.user)
        recipe.tags.add(sample_tag(self.user, 'test tag1'))

        tag_name_updated = 'test tag 2'
        new_tag = sample_tag(self.user, tag_name_updated)
        title_updated = 'test title 2'
        payload = {
            'title': title_updated,
            'tags': [new_tag.id, ]
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        tags = recipe.tags.all()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, title_updated)
        self.assertEqual(tags.count(), 1)
        self.assertIn(new_tag, tags)

    def test_complete_recipe_update(self):
        """ test that complete update work(put)."""
        recipe = sample_recipe(self.user)
        recipe.tags.add(sample_tag(self.user, 'test tag1'))

        payload = {
            'title': 'test recipe title',
            'time_minutes': 30,
            'price': 5.00
        }

        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 0)


class RecipeUploadImageTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@testmail.com',
            password='testPass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """ uploading image to recipe."""
        url = upload_image_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """ test bad request uploading image to recipe."""
        url = upload_image_url(self.recipe.id)
        res = self.client.post(url, {'image': 'not image'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
