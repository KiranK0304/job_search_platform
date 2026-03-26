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


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def auto_create_profile(sender, instance, created, **kwargs):
    """Automatically create a Profile for any new User, defaulting to seeker if not specified."""
    if created:
        Profile.objects.get_or_create(user=instance, defaults={"role": Profile.Role.SEEKER})