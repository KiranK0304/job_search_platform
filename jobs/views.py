from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from accounts.decorators import provider_required, seeker_required
from .models import Job, SavedJob


def job_list(request):
    """Show all active job listings with search and sort."""
    # Prevent providers from accessing the global job board
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == "provider":
        return redirect("provider_dashboard")

    jobs = Job.objects.filter(is_active=True)

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        jobs = jobs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(location__icontains=q)
        )

    # Sort
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'title':
        jobs = jobs.order_by('title', '-created_at')
    elif sort_by == 'location':
        jobs = jobs.order_by('location', '-created_at')
    else:
        jobs = jobs.order_by('-created_at')

    # For seekers: build applied map and saved set
    applied_map = {}
    saved_set = set()
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == "seeker":
        from applications.models import Application
        for app in Application.objects.filter(applicant=request.user).values("job_id", "id"):
            applied_map[app["job_id"]] = app["id"]
        saved_set = set(
            SavedJob.objects.filter(user=request.user).values_list("job_id", flat=True)
        )

    return render(request, "jobs/job_list.html", {
        "jobs": jobs,
        "applied_map": applied_map,
        "saved_set": saved_set,
        "search_query": q,
    })


def job_detail(request, job_id):
    """Show details of a single job."""
    job = get_object_or_404(Job, id=job_id)

    has_applied = False
    application_id = None
    is_saved = False
    if request.user.is_authenticated:
        app = job.applications.filter(applicant=request.user).first()
        if app:
            has_applied = True
            application_id = app.id
        is_saved = SavedJob.objects.filter(job=job, user=request.user).exists()

    return render(request, "jobs/job_detail.html", {
        "job": job,
        "has_applied": has_applied,
        "application_id": application_id,
        "is_saved": is_saved,
    })


@provider_required
def job_create(request):
    """Allow a provider to create a new job listing."""
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        location = request.POST.get("location", "")

        job = Job.objects.create(
            title=title,
            description=description,
            location=location,
            created_by=request.user,
        )
        return redirect("job_detail", job_id=job.id)

    return render(request, "jobs/job_create.html")


@provider_required
def job_delete(request, job_id):
    """Allow a provider to delete their own job listing."""
    job = get_object_or_404(Job, id=job_id)

    if job.created_by != request.user:
        return redirect("job_list")

    if request.method == "POST":
        job.delete()
        next_url = request.POST.get("next", "")
        if next_url:
            return redirect(next_url)
        return redirect("my_jobs")

    return render(request, "jobs/job_confirm_delete.html", {"job": job})


@provider_required
def my_jobs(request):
    """Show all jobs created by the logged-in provider."""
    jobs = Job.objects.filter(created_by=request.user).order_by("-created_at")
    return render(request, "jobs/my_jobs.html", {"jobs": jobs})


@seeker_required
def save_job(request, job_id):
    """Toggle save/unsave a job for a seeker."""
    job = get_object_or_404(Job, id=job_id)

    existing = SavedJob.objects.filter(job=job, user=request.user)
    if existing.exists():
        existing.delete()
    else:
        SavedJob.objects.create(job=job, user=request.user)

    next_url = request.POST.get("next", request.GET.get("next", ""))
    if next_url:
        return redirect(next_url)
    return redirect("job_list")


@seeker_required
def saved_jobs(request):
    """Show all jobs saved by the logged-in seeker."""
    saves = SavedJob.objects.filter(user=request.user).select_related("job", "job__created_by")

    # Build applied map
    from applications.models import Application
    applied_map = {}
    for app in Application.objects.filter(applicant=request.user).values("job_id", "id"):
        applied_map[app["job_id"]] = app["id"]

    return render(request, "jobs/saved_jobs.html", {
        "saves": saves,
        "applied_map": applied_map,
    })
