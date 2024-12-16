import pytest

from core.models.factories import UserFactory
from core.models.submission import Submission
from testing_utilities.base_view_test import ViewTest


class TestUploadsNoAuth(ViewTest):
    URL = "uploads"
    EXPECTED_STATUS = 200
    MAX_QUERIES = 2
    TEMPLATE = "registration/login.html"


class TestUploadAuth(ViewTest):
    URL = "uploads"
    EXPECTED_STATUS = 200
    TEMPLATE = "uploads.html"
    MAX_QUERIES = 11

    @pytest.fixture
    def as_user(self):
        return UserFactory()


class TestUploadDelete(ViewTest):
    URL = "uploads"
    EXPECTED_STATUS = 200
    TEMPLATE = "uploads.html"
    MAX_QUERIES = 11
    METHOD = "post"

    @pytest.fixture
    def as_user(self):
        return UserFactory()

    @pytest.fixture
    def submission(self, as_user):
        return Submission.objects.create(
            user=as_user, title="test", url="http://bing.com"
        )

    @pytest.fixture
    def request_kwargs(self, submission):
        """passed into test client"""
        return {"follow": True, "data": {"delete-upload": f"{submission.pk}"}}

    @pytest.fixture
    def response(self, submission, make_request):
        return make_request()
