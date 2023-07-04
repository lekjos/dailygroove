from typing import Any

from django.contrib import admin
from django.db.models import BooleanField, Count, ExpressionWrapper, Q, QuerySet
from django.http.request import HttpRequest

from core.models import Game, Player, Round


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "anonymous")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)
        return qs.annotate(
            anonymous=ExpressionWrapper(Q(name=None), output_field=BooleanField())
        )


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "player_count", "round_count")

    def player_count(self, obj):
        return obj.player_count

    def round_count(self, obj):
        return obj.round_count

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)
        return qs.annotate(
            player_count=Count("players", distinct=True),
            round_count=Count("round", distinct=True),
        )


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = (
        "round_number",
        "game",
        "winner",
    )
    search_fields = (
        "game__name",
        "player__name",
    )
