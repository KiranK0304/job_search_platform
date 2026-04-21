from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
import csv

from .models import Profile, SeekerProfile, ProviderProfile


def export_profiles_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=profiles_export.csv"

    writer = csv.writer(response)
    writer.writerow(
        [
            "username",
            "email",
            "role",
            "is_active",
            "is_verified",
            "is_flagged",
            "location",
            "created_at",
        ]
    )

    for profile in queryset.select_related("user"):
        writer.writerow(
            [
                profile.user.username,
                profile.user.email,
                profile.role,
                profile.user.is_active,
                profile.is_verified,
                profile.is_flagged,
                profile.location,
                profile.created_at,
            ]
        )
    return response


export_profiles_csv.short_description = "Export selected records as CSV"


@admin.action(description="Activate selected user accounts")
def activate_accounts(modeladmin, request, queryset):
    for profile in queryset.select_related("user"):
        profile.user.is_active = True
        profile.user.save(update_fields=["is_active"])


@admin.action(description="Deactivate selected user accounts")
def deactivate_accounts(modeladmin, request, queryset):
    for profile in queryset.select_related("user"):
        profile.user.is_active = False
        profile.user.save(update_fields=["is_active"])


@admin.action(description="Verify selected provider accounts")
def verify_providers(modeladmin, request, queryset):
    queryset.update(is_verified=True)


@admin.action(description="Flag selected accounts")
def flag_accounts(modeladmin, request, queryset):
    queryset.update(is_flagged=True, flagged_at=timezone.now())


@admin.action(description="Unflag selected accounts")
def unflag_accounts(modeladmin, request, queryset):
    queryset.update(is_flagged=False, flag_reason="", flagged_at=None)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "company_name",
        "location",
        "user_is_active",
        "is_verified",
        "is_flagged",
        "created_at",
    )
    list_filter = ("role", "is_verified", "is_flagged", "created_at")
    search_fields = (
        "user__username",
        "user__email",
        "company_name",
        "company_industry",
        "primary_skills",
    )
    readonly_fields = ("created_at",)
    actions = [
        activate_accounts,
        deactivate_accounts,
        verify_providers,
        flag_accounts,
        unflag_accounts,
        export_profiles_csv,
    ]

    @admin.display(boolean=True, description="Account Active")
    def user_is_active(self, obj):
        return obj.user.is_active


@admin.register(SeekerProfile)
class SeekerProfileAdmin(ProfileAdmin):
    list_display = (
        "user",
        "current_job_title",
        "primary_skills",
        "location",
        "user_is_active",
        "is_flagged",
        "created_at",
    )
    list_filter = ("is_flagged", "created_at", "seeker_industry", "job_type", "work_mode")
    search_fields = (
        "user__username",
        "user__email",
        "current_job_title",
        "primary_skills",
        "seeker_industry",
    )


@admin.register(ProviderProfile)
class ProviderProfileAdmin(ProfileAdmin):
    list_display = (
        "user",
        "company_name",
        "company_industry",
        "company_location",
        "user_is_active",
        "is_verified",
        "is_flagged",
        "created_at",
    )
    list_filter = ("is_verified", "is_flagged", "company_industry", "created_at")
    search_fields = (
        "user__username",
        "user__email",
        "company_name",
        "company_industry",
        "company_location",
    )
