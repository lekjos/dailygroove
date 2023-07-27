from django.test import RequestFactory

import pytest

from core.admin import UserAdminCustom

from ..utils.utilities import replace_url_params


@pytest.fixture
def test_request(url):
    factory = RequestFactory()
    return factory.get(url)


class AbstractTest:
    @pytest.fixture
    def url(self):
        return "/"


class TestReplaceUrlParams:
    class ContextNoParams(AbstractTest):
        def test_it_returns_empty_string_when_no_params(self, test_request):
            actual = replace_url_params(
                test_request,
            )
            assert actual == ""

    class ContextWithParams(AbstractTest):
        @pytest.fixture
        def url(self):
            return "/?param1=hi&param2=man"

        def test_it_returns_existing_params(self, test_request):
            actual = replace_url_params(
                test_request,
            )
            assert actual == "?param1=hi&param2=man"

    class ContextReplacesParams(AbstractTest):
        @pytest.fixture
        def url(self):
            return "/?param1=hi&param2=man"

        def test_it_replaces_existing_params(self, test_request):
            actual = replace_url_params(test_request, param2="bro")
            assert actual == "?param1=hi&param2=bro"

    class ContextSkipEncoding(AbstractTest):
        @pytest.fixture
        def url(self):
            return "/?param1=hi&param2=ma,n"

        def test_it_skips_encoding(self, test_request):
            actual = replace_url_params(test_request, skip_encode_params=["param2"])
            assert actual == "?param1=hi&param2=ma,n"

    class ContextWithEncoding(AbstractTest):
        @pytest.fixture
        def url(self):
            return "/?param1=hi&param2=ma,n"

        def test_it_encodes_param2(self, test_request):
            actual = replace_url_params(test_request)
            assert actual == "?param1=hi&param2=ma%2Cn"

    class ContextWithEmptyParam(AbstractTest):
        @pytest.fixture
        def url(self):
            return "/?param1=hi&param2="

        def test_it_deletes_param(self, test_request):
            actual = replace_url_params(test_request)
            assert actual == "?param1=hi"
