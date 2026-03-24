from django.db import models
from django.conf import settings


class Profile(models.Model):
    """
    Extends Django's built-in User model with marketplace-specific data.
    """

    class Role(models.TextChoices):
        SEEKER = "seeker", "Job Seeker"
        PROVIDER = "provider", "Job Provider"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
    )

    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "profiles"

    def __str__(self):
        return f"{self.user.username} ({self.role})"