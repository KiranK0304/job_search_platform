from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.contrib import messages

from .models import Profile
from .decorators import seeker_required, provider_required
from .forms import SeekerRegistrationForm, ProviderRegistrationForm
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
        form = SeekerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    form.save_profile(user)
                login(request, user)
                messages.success(request, "Account created successfully! Welcome to WorkBee.")
                return redirect("seeker_dashboard")
            except IntegrityError:
                form.add_error("username", "A user with that username already exists.")
        
        error = list(form.errors.values())[0][0] if form.errors else "Registration failed."
        return render(request, "accounts/register_seeker.html", {"error": error, "form_data": request.POST})

    return render(request, "accounts/register_seeker.html")


def register_provider(request):
    """Registration form for job providers."""
    if request.user.is_authenticated:
        return _dashboard_redirect(request.user)

    if request.method == "POST":
        form = ProviderRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    form.save_profile(user)
                login(request, user)
                messages.success(request, "Employer account created successfully!")
                return redirect("provider_dashboard")
            except IntegrityError:
                form.add_error("username", "A user with that username already exists.")
        
        error = list(form.errors.values())[0][0] if form.errors else "Registration failed."
        return render(request, "accounts/register_provider.html", {"error": error, "form_data": request.POST})

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
            messages.success(request, f"Welcome back, {user.username}!")
            return _dashboard_redirect(user)
        else:
            return render(request, "accounts/login.html", {
                "error": "Invalid username or password.",
                "form_data": request.POST
            })

    return render(request, "accounts/login.html")


# ─── Logout ───────────────────────────────────────────────────
def logout_view(request):
    """Log the user out."""
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("home")


# ─── Profile ──────────────────────────────────────────────────
@login_required
def profile_view(request):
    """Show and edit the logged-in user's profile."""
    profile = request.user.profile
    
    if request.method == "POST":
        user = request.user
        if 'first_name' in request.POST: user.first_name = request.POST['first_name']
        if 'last_name' in request.POST: user.last_name = request.POST['last_name']
        if 'email' in request.POST: user.email = request.POST['email']
        user.save()

        str_fields = [
            'phone_number', 'current_job_title', 'years_of_experience', 'primary_skills', 
            'seeker_industry', 'education', 'job_type', 'work_mode', 'expected_salary', 
            'notice_period', 'company_name', 'company_industry', 'company_size', 
            'company_location', 'company_website', 'company_description', 
            'recruiter_designation', 'linkedin_profile'
        ]
        
        for field in str_fields:
            if field in request.POST:
                val = request.POST[field]
                if field == 'years_of_experience':
                    if not val.strip():  # blank string
                        val = None
                    else:
                        try:
                            val = int(val)
                        except ValueError:
                            val = None # Handle bad integer types defensively
                setattr(profile, field, val)

        for file_field in ['profile_photo', 'resume', 'company_logo']:
            if file_field in request.FILES:
                setattr(profile, file_field, request.FILES[file_field])

        profile.save()
        messages.success(request, "Your profile has been successfully updated.")
        return redirect('profile')

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
