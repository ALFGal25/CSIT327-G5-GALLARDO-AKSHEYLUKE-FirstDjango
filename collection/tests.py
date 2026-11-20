from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Game, WantedGame

User = get_user_model()


class CartAndCaseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("akshey", password="pass12345")
        self.other = User.objects.create_user("other", password="pass12345")
        self.client.login(username="akshey", password="pass12345")

    def make_game(self, owner=None, **kwargs):
        data = dict(title="Super Mario World", platform="SNES", price=Decimal("1500.00"))
        data.update(kwargs)
        return Game.objects.create(owner=owner or self.user, **data)

    # --- account access
    def test_signup_creates_account(self):
        self.client.logout()
        r = self.client.post(reverse("signup"), {
            "username": "newbie", "email": "n@example.com",
            "first_name": "New", "last_name": "Bie",
            "password1": "Str0ngPass!word", "password2": "Str0ngPass!word",
        })
        self.assertRedirects(r, reverse("login"))
        self.assertTrue(User.objects.filter(username="newbie").exists())

    def test_pages_require_login(self):
        self.client.logout()
        for name in ["dashboard", "game_list", "search", "want_list", "profile"]:
            r = self.client.get(reverse(name))
            self.assertEqual(r.status_code, 302, name)
            self.assertIn(reverse("login"), r.url)

    def test_profile_page(self):
        self.assertContains(self.client.get(reverse("profile")), "akshey")

    # --- collection logging
    def test_add_edit_delete_game(self):
        r = self.client.post(reverse("game_add"), {
            "title": "Zelda", "platform": "N64", "condition": "MINT",
            "completeness": "CIB", "price": "2500.50",
        })
        self.assertRedirects(r, reverse("game_list"))
        game = Game.objects.get(title="Zelda")
        self.assertEqual(game.owner, self.user)

        self.client.post(reverse("game_edit", args=[game.pk]), {
            "title": "Zelda OoT", "platform": "N64", "condition": "GOOD",
            "completeness": "LOOSE", "price": "1000",
        })
        game.refresh_from_db()
        self.assertEqual(game.title, "Zelda OoT")

        self.client.post(reverse("game_delete", args=[game.pk]))
        self.assertFalse(Game.objects.filter(pk=game.pk).exists())

    def test_negative_price_rejected(self):
        r = self.client.post(reverse("game_add"), {
            "title": "Bad", "platform": "NES", "condition": "GOOD",
            "completeness": "LOOSE", "price": "-5",
        })
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Game.objects.filter(title="Bad").exists())

    def test_users_cannot_touch_each_others_games(self):
        theirs = self.make_game(owner=self.other, title="Secret")
        self.assertEqual(self.client.get(reverse("game_edit", args=[theirs.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("game_delete", args=[theirs.pk])).status_code, 404)
        self.assertNotContains(self.client.get(reverse("game_list")), "Secret")

    # --- search
    def test_search_finds_owned_game(self):
        self.make_game()
        r = self.client.get(reverse("search"), {"q": "mario"})
        self.assertContains(r, "Yes, you own 1 matching game")

    def test_search_platform_filter(self):
        self.make_game()
        r = self.client.get(reverse("search"), {"q": "mario", "platform": "N64"})
        self.assertContains(r, "Not in your collection")

    def test_search_ignores_other_users_games(self):
        self.make_game(owner=self.other)
        r = self.client.get(reverse("search"), {"q": "mario"})
        self.assertContains(r, "Not in your collection")

    # --- want list
    def test_want_list_add_and_prefill(self):
        r = self.client.get(reverse("want_add"), {"title": "Chrono Trigger", "platform": "SNES"})
        self.assertContains(r, "Chrono Trigger")
        self.client.post(reverse("want_add"), {
            "title": "Chrono Trigger", "platform": "SNES", "expected_price": "",
        })
        self.assertEqual(WantedGame.objects.filter(owner=self.user).count(), 1)

    def test_bought_moves_game_to_collection(self):
        w = WantedGame.objects.create(
            owner=self.user, title="Metroid", platform="NES", expected_price=Decimal("800"))
        r = self.client.post(reverse("want_bought", args=[w.pk]))
        game = Game.objects.get(title="Metroid")
        self.assertRedirects(r, reverse("game_edit", args=[game.pk]))
        self.assertEqual(game.price, Decimal("800"))
        self.assertFalse(WantedGame.objects.filter(pk=w.pk).exists())

    def test_bought_requires_post(self):
        w = WantedGame.objects.create(owner=self.user, title="X", platform="NES")
        self.assertEqual(self.client.get(reverse("want_bought", args=[w.pk])).status_code, 405)

    # --- value summary
    def test_dashboard_totals(self):
        self.make_game(title="A", price=Decimal("1000.00"))
        self.make_game(title="B", price=Decimal("2500.50"))
        self.make_game(owner=self.other, title="C", price=Decimal("99999"))
        WantedGame.objects.create(owner=self.user, title="W", platform="NES")
        r = self.client.get(reverse("dashboard"))
        self.assertEqual(r.context["owned_count"], 2)
        self.assertEqual(r.context["wanted_count"], 1)
        self.assertEqual(r.context["total_value"], Decimal("3500.50"))
        self.assertContains(r, "₱3,500.50")

    def test_dashboard_empty_value_is_zero(self):
        r = self.client.get(reverse("dashboard"))
        self.assertContains(r, "₱0.00")
