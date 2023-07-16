import pytest

from core.models.factories import GameFactory, PlayerFactory, SubmissionFactory
from core.models.round import Round


class TestRound:
    @pytest.fixture
    def game(self):
        return GameFactory()

    @pytest.fixture
    def player(self):
        return PlayerFactory()

    @pytest.fixture
    def existing_round(self, game, player, submissions):
        r = Round(game=game, submission=submissions[2], winner=player)
        r.save()
        return r

    @pytest.fixture
    def submissions(self, game):
        return SubmissionFactory.create_batch(5, games=[game])

    @pytest.mark.django_db
    def test_save_iterates_round_number(
        self,
        existing_round,
        submissions,
        player,
        game,
    ):
        round = Round(game=game, submission=submissions[2], winner=player)
        round.save()
        assert round.round_number == 2

    @pytest.mark.django_db
    def test_save_starts_round_zero(self, submissions, player, game):
        round = Round(game=game, submission=submissions[2], winner=player)
        round.save()
        assert round.round_number == 1
