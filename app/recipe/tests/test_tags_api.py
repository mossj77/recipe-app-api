from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe import serializers


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsAPITest(TestCase):
    """ test the public tags api"""

    def setUp(self):
        self.client = APIClient()

    def test_tag_list_unauthorized(self):
        """ test that not return any tag when unauthorized."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITest(TestCase):
    """ test the private tags api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@testmail.com',
            'testPassword'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """ test that authorized user can retrieve his tags successful. """
        Tag.objects.create(user=self.user, name='name1')
        Tag.objects.create(user=self.user, name='name2')
        tags = Tag.objects.all().order_by('-name')
        serializer = serializers.TagSerializer(tags, many=True)
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """ test that tags returned for authenticated user. """
        user2 = get_user_model().objects.create_user(
            'test2@testmail.com',
            'testPass'
        )
        Tag.objects.create(user=user2, name='name1')
        tag = Tag.objects.create(user=self.user, name='name2')
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """ test that tags create successful."""
        payload = {'name': 'testName'}
        res = self.client.post(TAGS_URL, payload)
        tag_exist = Tag.objects.all().filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(tag_exist)

    def test_create_tag_invalid(self):
        """ test that dont create a invalid tag."""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
