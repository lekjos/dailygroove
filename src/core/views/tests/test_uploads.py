import pytest

from core.models.factories import GameFactory, UserFactory
from test_utils.base_view_test import ViewTest


class TestUploadsNoAuth(ViewTest):
    URL = "uploads"
    EXPECTED_STATUS = 200
    TEMPLATE = "registration/login.html"


class TestUploadAuth(ViewTest):
    URL = "uploads"
    EXPECTED_STATUS = 200
    TEMPLATE = "uploads.html"
    MAX_QUERIES = 11

    @pytest.fixture
    def as_user(self):
        return UserFactory()
