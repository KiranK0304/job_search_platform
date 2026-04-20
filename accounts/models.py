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

    # shared
    phone_number = models.CharField(max_length=20, blank=True)

    # seeker specific
    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)
    current_job_title = models.CharField(max_length=150, blank=True)
    years_of_experience = models.PositiveIntegerField(null=True, blank=True)
    primary_skills = models.CharField(max_length=255, blank=True)
    seeker_industry = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=100, blank=True)
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)
    job_type = models.CharField(max_length=50, blank=True)
    work_mode = models.CharField(max_length=50, blank=True)
    expected_salary = models.CharField(max_length=100, blank=True)
    notice_period = models.CharField(max_length=100, blank=True)

    # provider specific
    company_name = models.CharField(max_length=150, blank=True)
    company_logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    company_industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    company_website = models.URLField(blank=True)
    company_location = models.CharField(max_length=200, blank=True)
    company_description = models.TextField(blank=True)
    recruiter_designation = models.CharField(max_length=100, blank=True)
    linkedin_profile = models.URLField(blank=True)

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