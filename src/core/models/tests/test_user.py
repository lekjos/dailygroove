from unittest import TestCase

from django.contrib.auth import get_user_model

import pytest

User = get_user_model()


@pytest.mark.django_db
class UsersManagersTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username="hello", email="normal@user.com", password="foo"
        )
        self.assertEqual(user.email, "normal@user.com")
        self.assertEqual(user.username, "hello")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(ValueError):
            User.objects.create_user(username="", email="")
        with self.assertRaises(ValueError):
            User.objects.create_user(username="", email="", password="foo")

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            username="super", email="super@user.com", password="foo"
        )
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertEqual(admin_user.username, "super")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username="super",
                email="super@user.com",
                password="foo",
                is_superuser=False,
            )
