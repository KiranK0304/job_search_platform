from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Profile
from .decorators import seeker_required, provider_required
from jobs.models import Job
from applications.models import Application


# ─── Helper: redirect user to correct dashboard ───────────────
def _dashboard_redirect(user):
    """Return the correct redirect based on the user's role."""
    if user.profile.role == "provider":
        return redirect("provider_dashboard")
    return redirect("seeker_dashboard")


# ─── Registration: choose role ────────────────────────────────
def choose_role(request):
    """Step 1: Ask the user to pick a role before registering."""
    if request.user.is_authenticated:
        return _dashboard_redirect(request.user)
    return render(request, "accounts/choose_role.html")


def register_seeker(request):
    """Registration form for job seekers."""
    if request.user.is_authenticated:
        return _dashboard_redirect(request.user)

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "accounts/register_seeker.html", {
                "error": "Username already taken."
            })

        user = User.objects.create_user(username=username, email=email, password=password)
        profile = user.profile
        profile.role = "seeker"
        profile.save()
        login(request, user)
        return redirect("seeker_dashboard")

    return render(request, "accounts/register_seeker.html")


def register_provider(request):
    """Registration form for job providers."""
    if request.user.is_authenticated:
        return _dashboard_redirect(request.user)

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "accounts/register_provider.html", {
                "error": "Username already taken."
            })

        user = User.objects.create_user(username=username, email=email, password=password)
        profile = user.profile
        profile.role = "provider"
        profile.save()
        login(request, user)
        return redirect("provider_dashboard")

    return render(request, "accounts/register_provider.html")


# ─── Login (with role-based redirect) ─────────────────────────
def login_view(request):
    """Handle user login — redirects to the correct dashboard."""
    if request.user.is_authenticated:
        return _dashboard_redirect(request.user)

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return _dashboard_redirect(user)
        else:
            return render(request, "accounts/login.html", {
                "error": "Invalid username or password."
            })

    return render(request, "accounts/login.html")


# ─── Logout ───────────────────────────────────────────────────
def logout_view(request):
    """Log the user out."""
    logout(request)
    return redirect("home")


# ─── Profile ──────────────────────────────────────────────────
@login_required
def profile_view(request):
    """Show the logged-in user's profile."""
    profile = Profile.objects.get(user=request.user)
    return render(request, "accounts/profile.html", {"profile": profile})


# ─── Seeker Dashboard ─────────────────────────────────────────
@seeker_required
def seeker_dashboard(request):
    """Dashboard for job seekers: recent applications + stats."""
    applications = Application.objects.filter(
        applicant=request.user
    ).select_related("job").order_by("-applied_at")[:5]

    total = Application.objects.filter(applicant=request.user).count()
    pending = Application.objects.filter(applicant=request.user, status="pending").count()
    accepted = Application.objects.filter(applicant=request.user, status="accepted").count()

    return render(request, "accounts/seeker_dashboard.html", {
        "applications": applications,
        "total": total,
        "pending": pending,
        "accepted": accepted,
    })


# ─── Provider Dashboard ───────────────────────────────────────
@provider_required
def provider_dashboard(request):
    """Dashboard for providers: their jobs + applicant stats."""
    jobs = Job.objects.filter(
        created_by=request.user
    ).order_by("-created_at")[:5]

    total_jobs = Job.objects.filter(created_by=request.user).count()
    active_jobs = Job.objects.filter(created_by=request.user, is_active=True).count()
    total_applicants = Application.objects.filter(
        job__created_by=request.user
    ).count()

    return render(request, "accounts/provider_dashboard.html", {
        "jobs": jobs,
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_applicants": total_applicants,
    })
