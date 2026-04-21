from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
import csv

from .models import (
    Job,
    SavedJob,
    JobCategory,
    Skill,
    IndustryType,
    EducationQualification,
)


def export_jobs_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=jobs_export.csv"
    writer = csv.writer(response)
    writer.writerow(
        [
            "title",
            "provider",
            "category",
            "location",
            "status",
            "moderation_status",
            "is_featured",
            "is_urgent",
            "created_at",
        ]
    )

    for job in queryset.select_related("created_by", "category"):
        writer.writerow(
            [
                job.title,
                job.created_by.username,
                job.category.name if job.category else "",
                job.location,
                job.status,
                job.moderation_status,
                job.is_featured,
                job.is_urgent,
                job.created_at,
            ]
        )
    return response


export_jobs_csv.short_description = "Export selected jobs as CSV"


@admin.action(description="Approve selected jobs")
def approve_jobs(modeladmin, request, queryset):
    queryset.update(moderation_status=Job.ModerationStatus.APPROVED)


@admin.action(description="Reject selected jobs")
def reject_jobs(modeladmin, request, queryset):
    queryset.update(moderation_status=Job.ModerationStatus.REJECTED)


@admin.action(description="Mark selected jobs as featured")
def mark_featured(modeladmin, request, queryset):
    queryset.update(is_featured=True)


@admin.action(description="Remove featured flag")
def unmark_featured(modeladmin, request, queryset):
    queryset.update(is_featured=False)


@admin.action(description="Mark selected jobs as urgent")
def mark_urgent(modeladmin, request, queryset):
    queryset.update(is_urgent=True)


@admin.action(description="Remove urgent flag")
def unmark_urgent(modeladmin, request, queryset):
    queryset.update(is_urgent=False)


@admin.action(description="Close selected jobs")
def close_jobs(modeladmin, request, queryset):
    queryset.update(
        status=Job.Status.CLOSED,
        is_active=False,
        closed_at=timezone.now(),
    )


@admin.action(description="Expire selected jobs")
def expire_jobs(modeladmin, request, queryset):
    queryset.update(status=Job.Status.EXPIRED, is_active=False)


@admin.action(description="Activate selected jobs")
def activate_jobs(modeladmin, request, queryset):
    queryset.update(status=Job.Status.ACTIVE, is_active=True)


@admin.action(description="Flag selected jobs")
def flag_jobs(modeladmin, request, queryset):
    queryset.update(is_flagged=True)


@admin.action(description="Unflag selected jobs")
def unflag_jobs(modeladmin, request, queryset):
    queryset.update(is_flagged=False, flag_reason="")


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "created_by",
        "category",
        "location",
        "status",
        "moderation_status",
        "is_featured",
        "is_urgent",
        "is_flagged",
        "created_at",
    )
    list_filter = (
        "status",
        "moderation_status",
        "is_featured",
        "is_urgent",
        "is_flagged",
        "category",
        "industry_type",
        "location",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "created_by__username",
        "created_by__email",
        "location",
        "industry",
    )
    autocomplete_fields = ("created_by", "category", "industry_type", "education_qualification", "skills")
    readonly_fields = ("created_at", "updated_at", "closed_at")
    actions = [
        approve_jobs,
        reject_jobs,
        mark_featured,
        unmark_featured,
        mark_urgent,
        unmark_urgent,
        close_jobs,
        expire_jobs,
        activate_jobs,
        flag_jobs,
        unflag_jobs,
        export_jobs_csv,
    ]
    date_hierarchy = "created_at"


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(IndustryType)
class IndustryTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(EducationQualification)
class EducationQualificationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "saved_at")
    search_fields = ("user__username", "job__title")
    date_hierarchy = "saved_at"
