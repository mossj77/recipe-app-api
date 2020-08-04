from django.test import TestCase

from django.contrib.auth import get_user_model


class UserModelTest(TestCase):

    def test_email_and_password_are_true_saved(self):
        """ test creating correct a user model."""
        test_email = 'test@testmail.com'
        test_password = 'TestPassword123'

        user = get_user_model().objects.create_user(
            email=test_email,
            password=test_password
        )

        self.assertEqual(user.email, test_email)
        self.assertTrue(user.check_password(test_password))

    def test_new_user_email_are_normalized(self):
        """ test a new user email address are normalized. """
        test_email = 'test@TESTMAIL.COM'
        user = get_user_model().objects.create_user(email=test_email,
                                                    password='TestPassword123')

        self.assertEqual(user.email, test_email.lower())

    def test_invalid_email(self):
        """ test dont create a user with invalid email. """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'pass123')

    def test_create_super_user(self):
        """ testing create correct a super user"""
        user = get_user_model().objects.create_superuser(
            email='test@testmail.com',
            password='TestPassword123')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
