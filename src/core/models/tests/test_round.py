from datetime import datetime, timedelta

from django.utils import timezone

import pytest
from freezegun import freeze_time

from core.models.factories import (
    GameFactory,
    PlayerFactory,
    RoundFactory,
    SubmissionFactory,
)
from core.models.game import Game
from core.models.round import Round


@pytest.fixture
def game(frequency):
    return GameFactory(frequency=frequency)


@pytest.fixture
def player():
    return PlayerFactory()


@pytest.fixture
def submissions(game):
    return SubmissionFactory.create_batch(5)


@pytest.fixture
def existing_round(game: Game, player, submissions):
    with freeze_time(
        datetime(year=2020, month=1, day=1, hour=11, tzinfo=game.timezone)
    ):
        return RoundFactory(game=game, submission=submissions[2], winner=player)


class TestRoundQuerySet:
    class ContextDaily:
        @pytest.fixture
        def frequency(self):
            return Game.Frequency.DAILY

        @pytest.mark.django_db
        def test_makes_one_new_round(self, game: Game, existing_round: Round):
            now = timezone.localtime(
                existing_round.datetime, timezone=game.timezone
            ) + timedelta(days=2)
            with freeze_time(now):
                Round.objects.current_round(game=game)
                current = Round.objects.current_round(game=game)
                expected = datetime.combine(
                    now.date(), game.round_start_time, tzinfo=game.timezone
                ) + timedelta(days=1)
                actual = current.round_ends_at
                assert expected == actual
                assert Round.objects.count() == 2


class TestRound:
    @pytest.fixture
    def frequency(self):
        return Game.Frequency.MANUAL

    @pytest.mark.django_db
    def test_save_iterates_round_number(
        self,
        existing_round,
        submissions,
        player,
        game,
    ):
        round = Round(game=game, submission=submissions[3], winner=player)
        round.save()
        assert round.round_number == 2

    @pytest.mark.django_db
    def test_save_starts_round_zero(self, submissions, player, game):
        round = Round(game=game, submission=submissions[2], winner=player)
        round.save()
        assert round.round_number == 1
