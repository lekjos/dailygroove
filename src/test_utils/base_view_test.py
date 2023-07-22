from django.test import Client
from django.urls import reverse

import pytest

from core.models.user import User


class ViewTest:
    URL = ""
    METHOD = "get"
    TEMPLATE = ""
    EXPECTED_STATUS = 200

    @pytest.fixture
    def as_user(self):
        return None

    @pytest.fixture
    def test_client(self, as_user: User, client: Client):
        if not as_user:
            return client
        client.force_login(as_user)
        return client

    @pytest.fixture
    def url_kwargs(self):
        return {}

    @pytest.fixture
    def url(self, url_kwargs):
        return reverse(self.URL, kwargs=url_kwargs)

    @pytest.fixture
    def response(self, test_client, url):
        method = getattr(test_client, self.METHOD)
        return method(url)

    @pytest.mark.django_db
    def test_returns_expected_status(self, client, response):
        assert response.status_code == self.EXPECTED_STATUS

    @pytest.mark.django_db
    def test_returns_correct_template(self, response):
        if not self.TEMPLATE:
            pytest.skip()
        assert self.TEMPLATE in [t.name for t in response.templates]
