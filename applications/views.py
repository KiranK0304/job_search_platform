from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages

from accounts.decorators import seeker_required, provider_required
from jobs.models import Job
from .models import Application


@seeker_required
def apply_to_job(request, job_id):
    """Allow a seeker to apply to a job."""
    job = get_object_or_404(Job, id=job_id)

    if not job.is_active:
        messages.error(request, "This job is no longer accepting applications.")
        return redirect("job_detail", job_id=job.id)

    # Already applied — bounce back
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.error(request, "You have already applied to this job.")
        return redirect("job_detail", job_id=job.id)

    if request.method == "POST":
        cover_letter = request.POST.get("cover_letter", "")
        Application.objects.create(
            job=job,
            applicant=request.user,
            cover_letter=cover_letter,
        )
        messages.success(request, "Your application has been submitted successfully!")
        # If came from job list page, go back there
        next_url = request.POST.get("next", "")
        if next_url:
            return redirect(next_url)
        return redirect("job_detail", job_id=job.id)

    return render(request, "applications/apply.html", {"job": job})


@seeker_required
def withdraw_application(request, app_id):
    """Allow a seeker to withdraw/delete their application."""
    application = get_object_or_404(Application, id=app_id)

    # Only the applicant can withdraw
    if application.applicant != request.user:
        return redirect("my_applications")

    if request.method == "POST":
        job_id = application.job.id
        application.delete()
        messages.success(request, "Application withdrawn successfully.")
        # If came from a specific page, go back there
        next_url = request.POST.get("next", "")
        if next_url:
            return redirect(next_url)
        return redirect("my_applications")

    return render(request, "applications/confirm_withdraw.html", {
        "application": application,
    })


@provider_required
def job_applications(request, job_id):
    """Show all applications for a specific job (provider who owns it)."""
    job = get_object_or_404(Job, id=job_id)

    if job.created_by != request.user:
        return HttpResponseForbidden("You are not allowed to view these applications.")

    applications = Application.objects.filter(job=job).order_by("-applied_at")
    return render(request, "applications/job_applications.html", {
        "job": job,
        "applications": applications,
    })


@seeker_required
def my_applications(request):
    """Show all applications submitted by the logged-in seeker."""
    applications = Application.objects.filter(
        applicant=request.user
    ).select_related("job", "job__created_by").order_by("-applied_at")

    # Status filter
    status_filter = request.GET.get('status', 'all')
    if status_filter in ['pending', 'accepted', 'rejected']:
        applications = applications.filter(status=status_filter)

    # Count by status for the tabs
    all_apps = Application.objects.filter(applicant=request.user)
    counts = {
        'all': all_apps.count(),
        'pending': all_apps.filter(status='pending').count(),
        'accepted': all_apps.filter(status='accepted').count(),
        'rejected': all_apps.filter(status='rejected').count(),
    }

    return render(request, "applications/my_applications.html", {
        "applications": applications,
        "status_filter": status_filter,
        "counts": counts,
    })


@provider_required
def update_application_status(request, app_id):
    """Allow a provider to accept or reject an application."""
    if request.method != "POST":
        return HttpResponseForbidden("Only POST requests are allowed.")

    application = get_object_or_404(Application, id=app_id)

    # Security check: only the job's creator can update the status
    if application.job.created_by != request.user:
        return HttpResponseForbidden("You are not allowed to update this application.")

    new_status = request.POST.get("status")
    if new_status in [Application.Status.ACCEPTED, Application.Status.REJECTED]:
        application.status = new_status
        # Bind feedback optionally
        if new_status == Application.Status.REJECTED:
            feedback = request.POST.get("feedback", "").strip()
            if feedback:
                application.feedback = feedback
        
        application.save()
        messages.success(request, f"Application status updated to {new_status}.")

    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url:
        return redirect(next_url)

    return redirect("job_applications", job_id=application.job.id)
