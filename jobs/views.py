from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages

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
        industry = request.POST.get("industry", "Not Specified")
        department = request.POST.get("department", "")
        job_type = request.POST.get("job_type", "Full-time")
        work_mode = request.POST.get("work_mode", "On-site")
        location = request.POST.get("location", "")
        
        try:
            vacancies = int(request.POST.get("vacancies", 1))
        except ValueError:
            vacancies = 1

        required_skills = request.POST.get("required_skills", "Not Specified")
        education = request.POST.get("education", "Not Specified")
        experience_level = request.POST.get("experience_level", "Entry Level")
        years_of_experience = request.POST.get("years_of_experience", "Not Specified")
        preferred_languages = request.POST.get("preferred_languages", "")
        certifications = request.POST.get("certifications", "")
        salary_type = request.POST.get("salary_type", "Negotiable")
        salary_range = request.POST.get("salary_range", "")
        salary_period = request.POST.get("salary_period", "Per Month")

        job = Job.objects.create(
            title=title,
            description=description,
            industry=industry,
            department=department,
            job_type=job_type,
            work_mode=work_mode,
            location=location,
            vacancies=vacancies,
            required_skills=required_skills,
            education=education,
            experience_level=experience_level,
            years_of_experience=years_of_experience,
            preferred_languages=preferred_languages,
            certifications=certifications,
            salary_type=salary_type,
            salary_range=salary_range,
            salary_period=salary_period,
            created_by=request.user,
        )
        messages.success(request, "Job created successfully!")
        return redirect("job_detail", job_id=job.id)

    return render(request, "jobs/job_create.html")


@provider_required
def job_delete(request, job_id):
    """Allow a provider to delete their own job listing."""
    job = get_object_or_404(Job, id=job_id)

    if job.created_by != request.user:
        return redirect("job_list")

    if request.method == "POST":
        job.is_active = False
        job.save()
        messages.success(request, "Job has been closed successfully.")
        next_url = request.POST.get("next", "")
        if next_url:
            return redirect(next_url)
        return redirect("my_jobs")

    return render(request, "jobs/job_confirm_delete.html", {"job": job})


@provider_required
def my_jobs(request):
    """Unified Dashboard showing all applications to the provider's jobs."""
    from applications.models import Application
    
    # All applications for jobs created by this provider
    applications = Application.objects.filter(
        job__created_by=request.user
    ).select_related("job", "applicant", "applicant__profile").order_by("-applied_at")

    # Fetch provider's active/total jobs just for the filter dropdown
    provider_jobs = Job.objects.filter(created_by=request.user)

    job_filter = request.GET.get('job_id', 'all')
    status_filter = request.GET.get('status', 'all')
    
    if job_filter != 'all':
        try:
            applications = applications.filter(job_id=int(job_filter))
        except ValueError:
            pass
            
    if status_filter in ['pending', 'accepted', 'rejected']:
        applications = applications.filter(status=status_filter)

    return render(request, "jobs/my_jobs.html", {
        "applications": applications,
        "provider_jobs": provider_jobs,
        "job_filter": str(job_filter),
        "status_filter": status_filter,
    })


@seeker_required
def save_job(request, job_id):
    """Toggle save/unsave a job for a seeker."""
    job = get_object_or_404(Job, id=job_id)

    existing = SavedJob.objects.filter(job=job, user=request.user)
    if existing.exists():
        existing.delete()
        messages.info(request, f"Removed '{job.title}' from saved jobs.")
    else:
        SavedJob.objects.create(job=job, user=request.user)
        messages.success(request, f"Job '{job.title}' saved successfully.")

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
