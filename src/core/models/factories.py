import uuid
import zoneinfo
from datetime import time

import factory
from factory.django import DjangoModelFactory

from core.models.game import Game
from core.models.player import Player
from core.models.round import Round
from core.models.submission import Submission
from core.models.user import User


class UserFactory(DjangoModelFactory):
    username = factory.Faker("name")
    email = factory.Faker("email")
    password = "test"

    class Meta:
        model = User
        django_get_or_create = ("email",)


class GameFactory(DjangoModelFactory):
    name = factory.Faker("word")
    owner = factory.RelatedFactory("core.models.factories.UserFactory")
    slug = factory.Faker("slug")
    frequency = Game.Frequency.MANUAL
    timezone = zoneinfo.ZoneInfo("America/New_York")
    round_start_time = time(hour=10)
    invite_token = uuid.uuid4()

    class Meta:
        model = Game
        django_get_or_create = ("slug",)

    @factory.post_generation
    def players(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for player in extracted:
                self.players.add(player)  # pylint: disable=no-member


class PlayerFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    name = None
    game = factory.SubFactory(GameFactory)

    class Meta:
        model = Player
        django_get_or_create = ("user",)


class SubmissionFactory(DjangoModelFactory):
    url = factory.Faker("url")
    title = factory.Faker("word")
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Submission


class RoundFactory(DjangoModelFactory):
    game = factory.SubFactory(GameFactory)
    winner = factory.SubFactory(PlayerFactory)
    moderator = factory.SubFactory(PlayerFactory)

    class Meta:
        model = Round

    @factory.post_generation
    def submissions(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for submission in extracted:
                self.submissions.add(submission)  # pylint: disable=no-member
                self.submissions.add(submission)  # pylint: disable=no-member
