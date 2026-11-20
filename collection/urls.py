from django.urls import path
from . import views

urlpatterns = [
    path("collection/", views.GameListView.as_view(), name="game_list"),
    path("collection/add/", views.GameCreateView.as_view(), name="game_add"),
    path("collection/<int:pk>/edit/", views.GameUpdateView.as_view(), name="game_edit"),
    path("collection/<int:pk>/delete/", views.GameDeleteView.as_view(), name="game_delete"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("wantlist/", views.WantListView.as_view(), name="want_list"),
    path("wantlist/add/", views.WantCreateView.as_view(), name="want_add"),
    path("wantlist/<int:pk>/delete/", views.WantDeleteView.as_view(), name="want_delete"),
    path("wantlist/<int:pk>/bought/", views.want_bought, name="want_bought"),
]
