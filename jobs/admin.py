from django.contrib import admin
from .models import Job, SavedJob


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "created_by", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "description")


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "saved_at")
    search_fields = ("user__username", "job__title")
    date_hierarchy = "saved_at"
