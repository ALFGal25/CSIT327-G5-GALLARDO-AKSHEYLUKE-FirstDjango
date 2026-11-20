from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView, DeleteView, ListView, TemplateView, UpdateView,
)

from .forms import GameForm, WantedGameForm
from .models import Game, Platform, WantedGame


class OwnerMixin(LoginRequiredMixin):
    """Every user only ever sees and changes their own records."""

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


# ---------------------------------------------------------------- collection
class GameListView(OwnerMixin, ListView):
    model = Game
    template_name = "collection/game_list.html"
    context_object_name = "games"


class GameCreateView(LoginRequiredMixin, CreateView):
    model = Game
    form_class = GameForm
    template_name = "collection/form.html"
    success_url = reverse_lazy("game_list")
    extra_context = {"heading": "Add a game"}

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, f"Added {form.instance.title} to your collection.")
        return super().form_valid(form)


class GameUpdateView(OwnerMixin, UpdateView):
    model = Game
    form_class = GameForm
    template_name = "collection/form.html"
    success_url = reverse_lazy("game_list")
    extra_context = {"heading": "Edit game"}

    def form_valid(self, form):
        messages.success(self.request, "Game updated.")
        return super().form_valid(form)


class GameDeleteView(OwnerMixin, DeleteView):
    model = Game
    template_name = "collection/confirm_delete.html"
    success_url = reverse_lazy("game_list")

    def form_valid(self, form):
        messages.success(self.request, "Game deleted.")
        return super().form_valid(form)


# -------------------------------------------------------------------- search
class SearchView(LoginRequiredMixin, TemplateView):
    """Answers the main question: "Do I already own this?"."""

    template_name = "collection/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "").strip()
        platform = self.request.GET.get("platform", "")
        searched = bool(q or platform)

        results = []
        if searched:
            results = Game.objects.filter(owner=self.request.user)
            if q:
                results = results.filter(title__icontains=q)
            if platform:
                results = results.filter(platform=platform)

        context.update(
            q=q,
            platform=platform,
            platforms=Platform.choices,
            searched=searched,
            results=results,
        )
        return context


# ------------------------------------------------------------------ want list
class WantListView(OwnerMixin, ListView):
    model = WantedGame
    template_name = "collection/want_list.html"
    context_object_name = "wanted"


class WantCreateView(LoginRequiredMixin, CreateView):
    model = WantedGame
    form_class = WantedGameForm
    template_name = "collection/form.html"
    success_url = reverse_lazy("want_list")
    extra_context = {"heading": "Add to want list"}

    def get_initial(self):
        # The search page links here with ?title=...&platform=... pre-filled.
        initial = super().get_initial()
        initial["title"] = self.request.GET.get("title", "")
        platform = self.request.GET.get("platform", "")
        if platform in Platform.values:
            initial["platform"] = platform
        return initial

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, f"Added {form.instance.title} to your want list.")
        return super().form_valid(form)


class WantDeleteView(OwnerMixin, DeleteView):
    model = WantedGame
    template_name = "collection/confirm_delete.html"
    success_url = reverse_lazy("want_list")

    def form_valid(self, form):
        messages.success(self.request, "Removed from your want list.")
        return super().form_valid(form)


@login_required
@require_POST
def want_bought(request, pk):
    """Move a wanted game into the collection once it has been bought."""
    wanted = get_object_or_404(WantedGame, pk=pk, owner=request.user)
    game = Game.objects.create(
        owner=request.user,
        title=wanted.title,
        platform=wanted.platform,
        price=wanted.expected_price or 0,
    )
    wanted.delete()
    messages.success(request, f"{game.title} moved to your collection. Fill in its details below.")
    return redirect("game_edit", pk=game.pk)
