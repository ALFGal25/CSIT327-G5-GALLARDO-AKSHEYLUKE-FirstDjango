from django import forms

from .models import Game, WantedGame


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ["title", "platform", "condition", "completeness", "price"]
        widgets = {"price": forms.NumberInput(attrs={"step": "0.01", "min": "0"})}


class WantedGameForm(forms.ModelForm):
    class Meta:
        model = WantedGame
        fields = ["title", "platform", "expected_price"]
        widgets = {"expected_price": forms.NumberInput(attrs={"step": "0.01", "min": "0"})}
