from .settings import *  # pylint: disable=unused-wildcard-import wildcard-import

ENV = "test"
DEBUG = False

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

WHITELISTED_EMAIL_DOMAINS = "knowndomain.com"  # for sign up view test
