from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminPageTest(TestCase):

    def setUp(self):
        """ set up a admin and user for test and login admin. """
        self.client = Client()
        self.admin = get_user_model().objects.create_superuser(
            email="testadmin@testmail.com",
            password="testAdminPassword123"
        )
        self.client.force_login(self.admin)

        self.user = get_user_model().objects.create_user(
            email="test@testmail.com",
            password="testPassword",
            name="test name"
        )

    def test_admin_page_users_list(self):
        """ test response of get user list api for admin."""
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)

    def test_user_change_page(self):
        """ test that the user edit page work. """
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_creat_user_page(self):
        """ test add user page that work."""
        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
