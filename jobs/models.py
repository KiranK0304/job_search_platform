from django.db import models
from django.conf import settings


class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Job categories"

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class IndustryType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class EducationQualification(models.Model):
    name = models.CharField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Job(models.Model):
    """
    Represents a job listing created by a provider.
    """

    class JobType(models.TextChoices):
        FULL_TIME = 'Full-time', 'Full-time'
        PART_TIME = 'Part-time', 'Part-time'
        CONTRACT = 'Contract', 'Contract'
        FREELANCE = 'Freelance', 'Freelance'
        INTERNSHIP = 'Internship', 'Internship'

    class WorkMode(models.TextChoices):
        ON_SITE = 'On-site', 'On-site'
        REMOTE = 'Remote', 'Remote'
        HYBRID = 'Hybrid', 'Hybrid'

    class ExperienceLevel(models.TextChoices):
        ENTRY = 'Entry Level', 'Entry Level'
        MID = 'Mid Level', 'Mid Level'
        SENIOR = 'Senior Level', 'Senior Level'

    class SalaryType(models.TextChoices):
        FIXED = 'Fixed', 'Fixed'
        RANGE = 'Range', 'Range'
        NEGOTIABLE = 'Negotiable', 'Negotiable'
        UNPAID = 'Unpaid', 'Unpaid'

    class SalaryPeriod(models.TextChoices):
        PER_HOUR = 'Per Hour', 'Per Hour'
        PER_MONTH = 'Per Month', 'Per Month'
        PER_YEAR = 'Per Year', 'Per Year'

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CLOSED = "closed", "Closed"

    class ModerationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    title = models.CharField(max_length=200)
    description = models.TextField()

    category = models.ForeignKey(
        JobCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs",
    )

    industry = models.CharField(max_length=100, default='Not Specified')
    industry_type = models.ForeignKey(
        IndustryType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs",
    )
    department = models.CharField(max_length=100, blank=True, null=True)

    job_type = models.CharField(max_length=50, choices=JobType.choices, default=JobType.FULL_TIME)
    work_mode = models.CharField(max_length=50, choices=WorkMode.choices, default=WorkMode.ON_SITE)
    location = models.CharField(max_length=100, blank=True)
    vacancies = models.IntegerField(default=1)

    required_skills = models.CharField(max_length=255, default='Not Specified')
    skills = models.ManyToManyField(Skill, blank=True, related_name="jobs")
    education = models.CharField(max_length=100, default='Not Specified')
    education_qualification = models.ForeignKey(
        EducationQualification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs",
    )
    experience_level = models.CharField(max_length=50, choices=ExperienceLevel.choices, default=ExperienceLevel.ENTRY)
    years_of_experience = models.CharField(max_length=50, default='Not Specified')
    preferred_languages = models.CharField(max_length=100, blank=True, null=True)
    certifications = models.CharField(max_length=100, blank=True, null=True)

    salary_type = models.CharField(max_length=50, choices=SalaryType.choices, default=SalaryType.NEGOTIABLE)
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    salary_period = models.CharField(max_length=50, choices=SalaryPeriod.choices, default=SalaryPeriod.PER_MONTH)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jobs",
    )

    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    moderation_status = models.CharField(
        max_length=10,
        choices=ModerationStatus.choices,
        default=ModerationStatus.APPROVED,
    )
    is_featured = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.TextField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

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