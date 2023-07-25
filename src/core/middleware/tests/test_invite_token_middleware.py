from unittest import mock
from uuid import uuid4

from django.test import RequestFactory
from django.urls import reverse

import pytest

from core.models.factories import GameFactory, PlayerFactory, UserFactory

from ..invite_token_middleware import InviteTokenMiddleware


class TestInviteTokenMiddlewareBase:
    @pytest.fixture
    def as_user(self):
        return None

    @pytest.fixture
    def game(self):
        return GameFactory()

    @pytest.fixture
    def player(self, game):
        return PlayerFactory(game=game)

    @pytest.fixture
    def invite_token(self, game):
        return game.invite_token

    @pytest.fixture
    def url(self):
        return reverse("dashboard")

    @pytest.fixture
    def token_request(self, url, as_user, invite_token):
        factory = RequestFactory()
        if invite_token:
            url = f"{url}?invite_token={invite_token}"
        request = factory.get(url)
        if as_user:
            request.user = as_user
        return request

    @pytest.fixture
    def get_response(self, token_request):
        def dummy_view(request):
            pass

        def make_request():
            middleware = InviteTokenMiddleware(get_response=dummy_view)
            return middleware.process_request(token_request)

        yield make_request


class TestInviteToken:
    class ContextAsAnon(TestInviteTokenMiddlewareBase):
        @pytest.mark.django_db
        def test_redirects_if_not_excluded_url(self, get_response, invite_token):
            response = get_response()
            assert response.status_code == 302
            assert (
                response.url == f"{reverse('login')}?invite_token={invite_token}&next=/"
            )

    class ContextAsNonPlayer(TestInviteTokenMiddlewareBase):
        @pytest.fixture
        def as_user(self):
            return UserFactory()

        @pytest.mark.django_db
        @mock.patch("core.middleware.invite_token_middleware.messages.success")
        def test_redirects_if_not_excluded_url(
            self, mock_message: mock.Mock, get_response, token_request, game
        ):
            get_response()
            mock_message.assert_called_once()
            mock_message.assert_called_with(
                token_request, f"You have been added to: {game.name}!"
            )

    class ContextAsPlayer(TestInviteTokenMiddlewareBase):
        @pytest.fixture
        def as_user(self, player):
            return player.user

        @pytest.mark.django_db
        @mock.patch("core.middleware.invite_token_middleware.messages.info")
        def test_redirects_if_not_excluded_url(
            self, mock_message: mock.Mock, get_response, token_request, game
        ):
            get_response()
            mock_message.assert_called_once_with(
                token_request, f"You are already a player in {game.name}!"
            )

    class ContextAsBadGame(TestInviteTokenMiddlewareBase):
        @pytest.fixture
        def as_user(self, player):
            return player.user

        @pytest.fixture
        def invite_token(self):
            return uuid4()

        @pytest.mark.django_db
        @mock.patch("core.middleware.invite_token_middleware.messages.error")
        def test_redirects_if_not_excluded_url(
            self, mock_message: mock.Mock, get_response, token_request
        ):
            get_response()
            mock_message.assert_called_once_with(
                token_request, f"Invalid game invite token"
            )

    class ContextExcludedUrl(TestInviteTokenMiddlewareBase):
        @pytest.fixture
        def url(self):
            return reverse("login")

        @pytest.fixture
        def invite_token(self):
            return uuid4()

        @pytest.mark.django_db
        def test_redirects_if_not_excluded_url(self, get_response):
            """No redirect on excluded urls"""
            response = get_response()

            assert response is None

    class ContextNoToken(TestInviteTokenMiddlewareBase):
        @pytest.fixture
        def invite_token(self):
            return None

        @pytest.mark.django_db
        def test_redirects_if_not_excluded_url(self, get_response):
            """No action if invite_token not included"""
            response = get_response()

            assert response is None
