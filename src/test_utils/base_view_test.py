from django.urls import reverse

import pytest


class ViewTest:
    URL = ""
    METHOD = "get"
    TEMPLATE = ""
    EXPECTED_STATUS = 200

    @pytest.fixture
    def url_kwargs(self):
        return {}

    @pytest.fixture
    def url(self, url_kwargs):
        return reverse(self.URL, kwargs=url_kwargs)

    @pytest.fixture
    def response(self, client, url):
        method = getattr(client, self.METHOD)
        return method(url)

    @pytest.mark.django_db
    def test_returns_expected_status(self, response):
        assert response.status_code == self.EXPECTED_STATUS

    @pytest.mark.django_db
    def test_returns_correct_template(self, response):
        if not self.TEMPLATE:
            pytest.skip()
        assert self.TEMPLATE in [t.name for t in response.templates]
