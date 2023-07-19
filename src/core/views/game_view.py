from functools import cached_property

from django.db.models import Count, F, OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin

from core.exceptions import NoEligibleSubmissionsError
from core.forms.winner_form import WinnerForm
from core.models.game import Game
from core.models.player import Player
from core.models.round import Round


class GameView(FormMixin, DetailView):
    model = Game
    form_class = WinnerForm
    template_name = "game-detail.html"
    raise_exception = True

    @cached_property
    def game(self):
        return get_object_or_404(Game, slug=self.kwargs["slug"])

    @cached_property
    def rounds(self):
        return (
            Round.objects.filter(game=self.game, winner__isnull=False)
            .annotate_game()
            .order_by("-datetime")
            .values(
                "round_number",
                "datetime",
                "winner_name",
                "submitted_by",
                "title",
                "url",
            )
        )

    @cached_property
    def current_round(self):
        try:
            return Round.objects.current_round(game=self.game)
        except NoEligibleSubmissionsError:
            return {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "title": "Out of Player Submissions!",
            }

    @cached_property
    def players(self):
        return (
            Player.objects.filter(game=self.game)
            .annotate_name()
            .annotate_most_recent_submission(self.game)
            .annotate_submission_count(self.game)
            .order_by("player_name")
            .values(
                "pk",
                "role",
                "user__id",
                "player_name",
                "most_recent_submission",
                "submission_count",
            )
        )

    @property
    def leader_board(self):
        recent_sqry = Subquery(
            Round.objects.filter(winner_id=OuterRef("pk"), game=self.game)
            .order_by("datetime")
            .values("datetime")[:1]
        )
        return (
            Player.objects.filter(game=self.game)
            .annotate_name()
            .annotate(
                win_count=Count(F("wins"), filter=Q(game=self.game), distinct=True),
                most_recent_win=recent_sqry,
            )
            .order_by("-win_count")
            .values("player_name", "win_count", "most_recent_win")
        )

    def get_moderator(self):
        is_moderator = [
            x
            for x in self.players
            if x["user__id"] == self.request.user.pk
            and (
                x["role"] == Player.Roles.MODERATOR
                or self.request.user.is_superuser
                or self.request.user.is_staff
            )
        ]

        return is_moderator[0] if is_moderator else None

    def get_form(self, form_class=None):
        moderator = self.get_moderator()
        if moderator:
            moderator = moderator["pk"]

        return WinnerForm(
            instance=self.current_round,
            players=self.players,
            moderator_id=moderator,
            **self.get_form_kwargs(),
        )

    def get_success_url(self) -> str:
        return reverse("game-view", kwargs={"slug": self.kwargs["slug"]})

    def get_object(self, *args, **kwargs):
        return self.game

    def get_context_data(self, **kwargs):
        if "form" not in kwargs:
            kwargs["form"] = self.get_form()
        context = kwargs
        context["object"] = self.game
        context["page_title"] = self.game.name
        context["leader_board"] = self.leader_board
        context["rounds"] = self.rounds
        context["current_round"] = self.current_round
        context["players"] = self.players
        context["moderator"] = self.get_moderator()
        return context

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""

        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        action = request.POST.get("action")
        if form.is_valid() and action == "declare_winner":
            form.save()
            return self.form_valid(form)
        if form.is_valid() and action == "reveal":
            return self.render_to_response(
                self.get_context_data(
                    form=form,
                    submitted_by=self.current_round.submission.user.get_display_name(),
                )
            )
        return self.form_invalid(form)

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)
