from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from collection.models import Game
from collection.utils import collection_summary


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update(collection_summary(user))
        context["recent_games"] = Game.objects.filter(owner=user).order_by("-created_at")[:5]
        return context
