from functools import cached_property
from typing import Dict

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Count, F, OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin

from core.exceptions import NoEligibleSubmissionsError
from core.forms.winner_form import WinnerForm
from core.models.game import Game
from core.models.player import Player
from core.models.round import Round
from core.models.submission import Submission


class GameView(FormMixin, DetailView):
    model = Game
    form_class = WinnerForm
    template_name = "game-detail.html"
    raise_exception = True

    @property
    def game(self):
        return get_object_or_404(Game, slug=self.kwargs["slug"])

    @property
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
            )[:50]
        )

    @property
    def current_round(self):
        try:
            return Round.objects.current_round(game=self.game)
        except NoEligibleSubmissionsError:
            submission = Submission(
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                title="Out of Player Submissions!",
            )
            return Round(game=self.game, submission=submission)

    @property
    def players(self):
        return (
            Player.objects.filter(game=self.game, disabled=False)
            .annotate_name()
            .annotate_most_recent_submission()
            .annotate_submission_count()
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
            .order_by("-datetime")
            .values("datetime")[:1]
        )
        return (
            Player.objects.filter(game=self.game, disabled=False)
            .annotate_name()
            .annotate(
                win_count=Count(F("wins"), filter=Q(game=self.game), distinct=True),
                most_recent_win=recent_sqry,
            )
            .filter(win_count__gt=0)
            .order_by("-win_count")
            .values("player_name", "win_count", "most_recent_win")
        )

    @property
    def moderator(self) -> Dict[str, str]:
        moderators = [
            x
            for x in self.players
            if x["user__id"] == self.request.user.pk
            and (
                x["role"] == Player.Roles.MODERATOR
                or self.request.user.is_staff
                or self.request.user.is_superuser
            )
        ]
        if moderators:
            return moderators[0]
        return None

    def get_form(self, form_class=None):
        moderator = self.moderator
        if moderator:
            moderator = moderator["pk"]

        return WinnerForm(
            instance=self.current_round,
            players=self.players,
            moderator_id=moderator,
            **self.get_form_kwargs(),
        )

    def get_success_url(self) -> str:
        return reverse("game_detail", kwargs={"slug": self.kwargs["slug"]})

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
        context["players"] = [x for x in self.players if x["submission_count"]]
        context["wall_of_shame"] = [
            x["player_name"] for x in self.players if not x["submission_count"]
        ]
        context["moderator"] = self.moderator
        return context

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""

        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        if not self.moderator:
            raise PermissionDenied("Only moderators and owners can POST.")
        form = self.get_form()
        action = request.POST.get("action")
        if form.is_valid():
            if action == "Declare Winner":
                form.save()
                return self.form_valid(form)
            if action == "Reveal Submitter":
                return self.render_to_response(
                    self.get_context_data(
                        form=form,
                        submitted_by=self.current_round.submission.user.get_display_name(),
                    )
                )
            try:
                if action == "Shuffle":
                    self.current_round.shuffle()
                    return self.render_to_response(self.get_context_data(form=form))
                if action == "Start Next Round":
                    Round.objects.create(game=self.game)
            except NoEligibleSubmissionsError:
                messages.error(self.request, "There are no more submissions!")
            return redirect("game_detail", slug=self.game.slug)

        return self.form_invalid(form)

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)
