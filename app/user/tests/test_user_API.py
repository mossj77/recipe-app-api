from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_user_created_successful(self):
        """ test that creation of valid user is successful."""
        payload = {
            'email': 'test@testmail.com',
            'password': 'testPass123',
            'name': 'testName'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_create_user_that_exist(self):
        """ test that dont create the user that exist now. """
        payload = {
            'email': 'test@testmail.com',
            'password': 'testPass123'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ test dont create a user whit short password (less than 5 char)"""
        payload = {
            'email': 'test@testmail.com',
            'password': 'test'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exist)

    def test_token_create_for_user(self):
        """ test that token successful created whit correct payload. """
        payload = {'email': 'test@testmail.com', 'password': 'testPass'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_token_password_is_wrong(self):
        """ test that token not created when pass is wrong."""
        create_user(**{'email': 'test@testmail.com', 'password': 'testPass'})
        payload = {'email': 'test@testmail.com', 'password': 'wrongPass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_user_not_exist(self):
        """test that token not created when user not existed."""
        payload = {'email': 'test@testmail.com', 'password': 'testPass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_missing_field(self):
        """ test that token not created when a field is null."""
        create_user(**{'email': 'test@testmail.com', 'password': 'testPass'})
        payload = {'email': 'test@testmail.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """ test that cant access to user update when is unauthorized."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@testmail.com',
            password='testPass',
            name='testName'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_authorized(self):
        """ test that user can retrieve when authorized. """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_post_not_allowed(self):
        """ test that POST method not allowed for me api. """
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_profile_update(self):
        """ test that authorized user can update his profile. """
        payload = {'name': 'new name', 'password': 'newTestPass'}
        res = self.client.patch(ME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
