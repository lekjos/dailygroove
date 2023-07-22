from django.conf import settings


def test_not_debug():
    assert settings.DEBUG == False
