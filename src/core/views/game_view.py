from django.views.generic import DetailView

from ..models.game import Game


class GameView(DetailView):
    model = Game
    template_name = "game-detail.html"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.object.name
