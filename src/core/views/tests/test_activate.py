from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

import pytest

from core.models.factories import UserFactory
from core.tokens import account_activation_token
from testing_utilities.base_view_test import ViewTest


class TestActivateInvalid(ViewTest):
    URL = "activate"
    URL_KWARGS = {"uidb64": "asdfasdf", "token": "asdfasdfa"}
    TEMPLATE = "account_activation_invalid.html"
    MAX_QUERIES = 3

    @pytest.fixture
    def url_kwargs(self):
        return {"uidb64": "asdfasdf", "token": "asdfasdfa"}


class TestActivateValid(ViewTest):
    URL = "activate"
    EXPECTED_STATUS = 200
    TEMPLATE = "dashboard.html"
    MAX_QUERIES = 101

    @pytest.fixture(autouse=True)
    def user(self):
        return UserFactory()

    @pytest.fixture
    def url_kwargs(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        return {"uidb64": uid, "token": token}
