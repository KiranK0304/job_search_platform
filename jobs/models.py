from django.db import models
from django.conf import settings


class Job(models.Model):
    """
    Represents a job listing created by a provider.
    """

    title = models.CharField(max_length=200)
    description = models.TextField()

    location = models.CharField(max_length=100, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jobs",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "jobs"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class SavedJob(models.Model):
    """A job bookmarked/saved by a seeker for later."""

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="saves",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_jobs",
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "saved_jobs"
        unique_together = ("job", "user")
        ordering = ["-saved_at"]

    def __str__(self):
        return f"{self.user} saved {self.job}"