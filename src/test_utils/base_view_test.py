from django.test import Client
from django.urls import reverse

import pytest

from core.models.user import User


class ViewTest:
    URL = ""
    METHOD = "get"
    TEMPLATE = ""
    EXPECTED_STATUS = 200
    MAX_QUERIES = 1

    @pytest.fixture
    def as_user(self):
        return None

    @pytest.fixture
    def test_client(self, as_user: User):
        client = Client(enforce_csrf_checks=False)
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
    def request_kwargs(self):
        """passed into test client"""
        return {"follow": True}

    @pytest.fixture
    def make_request(
        self,
        test_client: Client,
        url,
        request_kwargs: dict,
    ):
        def perform_web_request():
            method = getattr(test_client, self.METHOD)
            return method(url, **request_kwargs)

        yield perform_web_request

    @pytest.fixture
    def response(self, make_request):
        return make_request()

    @pytest.mark.django_db
    def test_returns_expected_status(self, response):
        expected = self.EXPECTED_STATUS
        actual = response.status_code
        assert expected == actual

    @pytest.mark.django_db
    def test_returns_correct_template(self, response):
        if not self.TEMPLATE:
            pytest.skip()
        assert self.TEMPLATE in [t.name for t in response.templates]

    @pytest.mark.django_db
    def test_it_max_queries_not_exceeded(
        self, make_request, django_assert_max_num_queries
    ):
        if not self.MAX_QUERIES:
            pytest.skip()

        with django_assert_max_num_queries(self.MAX_QUERIES) as num_queries:
            make_request()
            assert len(num_queries) < self.MAX_QUERIES
