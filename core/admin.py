from django.contrib import admin
from django.contrib.auth import get_user_model
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone
from datetime import timedelta

from accounts.models import Profile
from applications.models import Application
from jobs.models import Job
from .models import Report


@admin.action(description="Mark reports as In Review")
def mark_in_review(modeladmin, request, queryset):
	queryset.update(status=Report.Status.IN_REVIEW)


@admin.action(description="Resolve reports")
def resolve_reports(modeladmin, request, queryset):
	queryset.update(
		status=Report.Status.RESOLVED,
		action_taken=Report.ActionTaken.WARN,
		handled_by=request.user,
		resolved_at=timezone.now(),
	)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
	list_display = (
		"target_type",
		"target_id",
		"reason",
		"status",
		"action_taken",
		"reported_by",
		"handled_by",
		"created_at",
	)
	list_filter = ("target_type", "status", "action_taken", "created_at")
	search_fields = ("reason", "details", "reported_by__username")
	readonly_fields = ("created_at",)
	actions = [mark_in_review, resolve_reports]
	date_hierarchy = "created_at"


def admin_dashboard_view(request):
	now = timezone.now()
	week_start = now - timedelta(days=7)
	month_start = now - timedelta(days=30)
	day_start = now - timedelta(days=1)

	User = get_user_model()

	recent_activity = []
	for user in User.objects.order_by("-date_joined")[:5]:
		recent_activity.append(
			{
				"time": user.date_joined,
				"label": f"New user registered: {user.username}",
			}
		)
	for job in Job.objects.select_related("created_by").order_by("-created_at")[:5]:
		recent_activity.append(
			{
				"time": job.created_at,
				"label": f"New job posted: {job.title} by {job.created_by.username}",
			}
		)
	for app in Application.objects.select_related("applicant", "job").order_by("-applied_at")[:5]:
		recent_activity.append(
			{
				"time": app.applied_at,
				"label": f"Application submitted by {app.applicant.username} for {app.job.title}",
			}
		)
	for report in Report.objects.order_by("-created_at")[:5]:
		recent_activity.append(
			{
				"time": report.created_at,
				"label": f"Report created: {report.get_target_type_display()} #{report.target_id}",
			}
		)

	recent_activity = sorted(recent_activity, key=lambda item: item["time"], reverse=True)[:12]

	context = {
		**admin.site.each_context(request),
		"title": "WorkBee Admin Dashboard",
		"total_seekers": Profile.objects.filter(role=Profile.Role.SEEKER).count(),
		"total_providers": Profile.objects.filter(role=Profile.Role.PROVIDER).count(),
		"jobs_active": Job.objects.filter(status=Job.Status.ACTIVE).count(),
		"jobs_expired": Job.objects.filter(status=Job.Status.EXPIRED).count(),
		"jobs_closed": Job.objects.filter(status=Job.Status.CLOSED).count(),
		"total_applications": Application.objects.count(),
		"new_users_daily": User.objects.filter(date_joined__gte=day_start).count(),
		"new_users_weekly": User.objects.filter(date_joined__gte=week_start).count(),
		"new_users_monthly": User.objects.filter(date_joined__gte=month_start).count(),
		"open_reports": Report.objects.filter(status=Report.Status.OPEN).count(),
		"recent_activity": recent_activity,
	}
	return TemplateResponse(request, "admin/dashboard.html", context)


original_get_urls = admin.site.get_urls


def get_urls():
	urls = original_get_urls()
	custom_urls = [
		path("dashboard/", admin.site.admin_view(admin_dashboard_view), name="workbee_dashboard"),
	]
	return custom_urls + urls


admin.site.get_urls = get_urls

