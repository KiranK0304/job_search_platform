from django.conf import settings
from django.db import models


class Report(models.Model):
	class TargetType(models.TextChoices):
		USER = "user", "User"
		JOB = "job", "Job"
		APPLICATION = "application", "Application"

	class Status(models.TextChoices):
		OPEN = "open", "Open"
		IN_REVIEW = "in_review", "In Review"
		RESOLVED = "resolved", "Resolved"
		REJECTED = "rejected", "Rejected"

	class ActionTaken(models.TextChoices):
		NONE = "none", "No Action"
		WARN = "warn", "Warn"
		SUSPEND = "suspend", "Suspend"
		DELETE = "delete", "Delete"

	target_type = models.CharField(max_length=20, choices=TargetType.choices)
	target_id = models.PositiveIntegerField()
	reason = models.CharField(max_length=255)
	details = models.TextField(blank=True)

	reported_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="submitted_reports",
	)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
	action_taken = models.CharField(
		max_length=20,
		choices=ActionTaken.choices,
		default=ActionTaken.NONE,
	)
	handled_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="handled_reports",
	)

	created_at = models.DateTimeField(auto_now_add=True)
	resolved_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.get_target_type_display()} #{self.target_id} - {self.reason}"
