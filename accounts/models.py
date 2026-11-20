from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """The only role in Cart & Case is the Collector, so no extra fields are needed."""

    def __str__(self):
        return self.username
