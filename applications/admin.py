from django.contrib import admin
from django.http import HttpResponse
import csv

from .models import Application


def export_applications_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=applications_export.csv"
    writer = csv.writer(response)
    writer.writerow(
        [
            "job",
            "provider",
            "applicant",
            "status",
            "is_flagged",
            "applied_at",
        ]
    )

    for app in queryset.select_related("job", "job__created_by", "applicant"):
        writer.writerow(
            [
                app.job.title,
                app.job.created_by.username,
                app.applicant.username,
                app.status,
                app.is_flagged,
                app.applied_at,
            ]
        )
    return response


export_applications_csv.short_description = "Export selected applications as CSV"


@admin.action(description="Mark as shortlisted")
def mark_shortlisted(modeladmin, request, queryset):
    queryset.update(status=Application.Status.SHORTLISTED)


@admin.action(description="Mark as rejected")
def mark_rejected(modeladmin, request, queryset):
    queryset.update(status=Application.Status.REJECTED)


@admin.action(description="Mark as hired")
def mark_hired(modeladmin, request, queryset):
    queryset.update(status=Application.Status.HIRED)


@admin.action(description="Flag selected applications")
def flag_applications(modeladmin, request, queryset):
    queryset.update(is_flagged=True)


@admin.action(description="Unflag selected applications")
def unflag_applications(modeladmin, request, queryset):
    queryset.update(is_flagged=False, flag_reason="")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "applicant",
        "job",
        "provider",
        "status",
        "is_flagged",
        "applied_at",
        "updated_at",
    )
    list_filter = ("status", "is_flagged", "applied_at", "job__created_by")
    search_fields = (
        "applicant__username",
        "applicant__email",
        "job__title",
        "job__created_by__username",
    )
    readonly_fields = ("applied_at", "updated_at")
    autocomplete_fields = ("job", "applicant")
    actions = [
        mark_shortlisted,
        mark_rejected,
        mark_hired,
        flag_applications,
        unflag_applications,
        export_applications_csv,
    ]
    date_hierarchy = "applied_at"

    @admin.display(description="Provider")
    def provider(self, obj):
        return obj.job.created_by
