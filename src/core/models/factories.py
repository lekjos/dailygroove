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
        django_get_or_create = ("username",)


class PlayerFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    name = None

    class Meta:
        model = Player
        django_get_or_create = ("user",)


class GameFactory(DjangoModelFactory):
    name = factory.Faker("word")
    owner = factory.SubFactory(PlayerFactory)
    slug = factory.Faker("slug")

    class Meta:
        model = Game
        django_get_or_create = ("slug",)

    @factory.post_generation
    def submissions(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for submission in extracted:
                self.submissions.add(submission)  # pylint: disable=no-member

    @factory.post_generation
    def players(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for player in extracted:
                self.players.add(player)  # pylint: disable=no-member


class SubmissionFactory(DjangoModelFactory):
    url = factory.Faker("url")
    title = factory.Faker("word")
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Submission

    @factory.post_generation
    def games(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for game in extracted:
                self.games.add(game)  # pylint: disable=no-member


class RoundFactory(DjangoModelFactory):
    # winner = factory.SubFactory(PlayerFactory)
    # submission = factory.SubFactory(SubmissionFactory)
    # moderator = factory.SubFactory(PlayerFactory)
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
