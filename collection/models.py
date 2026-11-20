from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Platform(models.TextChoices):
    NES = "NES", "NES"
    SNES = "SNES", "Super Nintendo (SNES)"
    N64 = "N64", "Nintendo 64"
    GAMECUBE = "GC", "GameCube"
    GAMEBOY = "GB", "Game Boy"
    GBC = "GBC", "Game Boy Color"
    GBA = "GBA", "Game Boy Advance"
    NDS = "NDS", "Nintendo DS"
    GENESIS = "GEN", "Sega Genesis / Mega Drive"
    SATURN = "SAT", "Sega Saturn"
    DREAMCAST = "DC", "Sega Dreamcast"
    PS1 = "PS1", "PlayStation"
    PS2 = "PS2", "PlayStation 2"
    PSP = "PSP", "PSP"
    ATARI = "ATARI", "Atari 2600"
    OTHER = "OTHER", "Other"


class Game(models.Model):
    """A game the collector OWNS."""

    class Condition(models.TextChoices):
        MINT = "MINT", "Mint"
        NEAR_MINT = "NEARMINT", "Near Mint"
        GOOD = "GOOD", "Good"
        FAIR = "FAIR", "Fair"
        POOR = "POOR", "Poor"

    class Completeness(models.TextChoices):
        LOOSE = "LOOSE", "Loose (cartridge/disc only)"
        CIB = "CIB", "Complete in box"
        SEALED = "SEALED", "Sealed"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="games"
    )
    title = models.CharField(max_length=150)
    platform = models.CharField(max_length=10, choices=Platform.choices)
    condition = models.CharField(
        max_length=10, choices=Condition.choices, default=Condition.GOOD
    )
    completeness = models.CharField(
        max_length=10, choices=Completeness.choices, default=Completeness.LOOSE
    )
    price = models.DecimalField(
        "Estimated price (₱)",
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.get_platform_display()})"


class WantedGame(models.Model):
    """A game the collector does NOT own yet."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wanted_games"
    )
    title = models.CharField(max_length=150)
    platform = models.CharField(max_length=10, choices=Platform.choices)
    expected_price = models.DecimalField(
        "Expected price (₱)",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.get_platform_display()})"
