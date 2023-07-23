from django.urls import reverse

import pytest

from core.models.factories import GameFactory, UserFactory
from test_utils.base_view_test import ViewTest


class TestSignUpGet(ViewTest):
    URL = "signup"
    EXPECTED_STATUS = 200
    TEMPLATE = "signup.html"


class TestSignUpPostInvalid(ViewTest):
    URL = "signup"
    EXPECTED_STATUS = 200
    METHOD = "post"
    TEMPLATE = "signup.html"


class TestSignUpPostValid(ViewTest):
    URL = "signup"
    EXPECTED_STATUS = 302
    METHOD = "post"
    MAX_QUERIES = 5

    @pytest.fixture
    def request_kwargs(self):
        """passed into test client"""
        return {
            "data": {
                "username": "testman",
                "email": "test@test.com",
                "password1": "aStrong1pw;",
                "password2": "aStrong1pw;",
            },
        }

    @pytest.mark.django_db
    def test_it_redirects_to_correct_page(self, response):
        assert response.url == reverse("account_activation_sent")
