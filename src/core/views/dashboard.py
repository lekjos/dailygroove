from django.db.models import Q
from django.views.generic import TemplateView

from ..models.game import Game


class Dashboard(TemplateView):
    template_name = "dashboard.html"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["user"] = user
        if self.request.user.is_authenticated:
            context["active_games"] = Game.objects.filter(
                Q(players__pk=user.pk) | Q(owner_id=user.pk)
            ).distinct()
        return context
