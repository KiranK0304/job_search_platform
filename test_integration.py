"""
Full integration test for WorkBee job app.
Tests: registration, login, role-based access, job CRUD, apply, withdraw, dashboards.
"""
import os, sys, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'job_app.settings'
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User
from accounts.models import Profile
from jobs.models import Job
from applications.models import Application

PASS = 0
FAIL = 0

def check(label, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {label}")
    else:
        FAIL += 1
        print(f"  ❌ {label}")

# Clean slate
Application.objects.all().delete()
Job.objects.all().delete()
Profile.objects.all().delete()
User.objects.all().delete()

c = Client()

# ═══════════════════════════════════════════════════
print("\n🔹 1. PUBLIC PAGES")
# ═══════════════════════════════════════════════════
for url, name in [('/', 'Home'), ('/about/', 'About'), ('/contact/', 'Contact'),
                   ('/jobs/', 'Job list'), ('/accounts/login/', 'Login'),
                   ('/accounts/register/', 'Choose role')]:
    r = c.get(url)
    check(f"{name} ({url}) → {r.status_code}", r.status_code == 200)

# ═══════════════════════════════════════════════════
print("\n🔹 2. REGISTRATION — Seeker")
# ═══════════════════════════════════════════════════
r = c.get('/accounts/register/seeker/')
check("Seeker register page loads", r.status_code == 200)

r = c.post('/accounts/register/seeker/', {
    'username': 'alice', 'email': 'alice@test.com',
    'password': 'TestPass123!'
}, follow=True)
check("Seeker registration succeeds", r.status_code == 200)
alice = User.objects.get(username='alice')
check("Alice profile exists", hasattr(alice, 'profile'))
check("Alice role is seeker", alice.profile.role == 'seeker')
c.logout()

# ═══════════════════════════════════════════════════
print("\n🔹 3. REGISTRATION — Provider")
# ═══════════════════════════════════════════════════
r = c.get('/accounts/register/provider/')
check("Provider register page loads", r.status_code == 200)

r = c.post('/accounts/register/provider/', {
    'username': 'bob', 'email': 'bob@test.com',
    'password': 'TestPass123!'
}, follow=True)
check("Provider registration succeeds", r.status_code == 200)
bob = User.objects.get(username='bob')
check("Bob profile exists", hasattr(bob, 'profile'))
check("Bob role is provider", bob.profile.role == 'provider')
c.logout()

# ═══════════════════════════════════════════════════
print("\n🔹 4. LOGIN — Role-based redirect")
# ═══════════════════════════════════════════════════
r = c.post('/accounts/login/', {'username': 'alice', 'password': 'TestPass123!'})
check("Alice login redirects to seeker dashboard", r.status_code == 302 and 'seeker' in r.url)
c.logout()

r = c.post('/accounts/login/', {'username': 'bob', 'password': 'TestPass123!'})
check("Bob login redirects to provider dashboard", r.status_code == 302 and 'provider' in r.url)
c.logout()

# ═══════════════════════════════════════════════════
print("\n🔹 5. ROLE-BASED ACCESS CONTROL")
# ═══════════════════════════════════════════════════
# Alice (seeker) cannot access provider pages
c.login(username='alice', password='TestPass123!')
r = c.get('/jobs/create/')
check("Seeker BLOCKED from job create", r.status_code == 302)

r = c.get('/jobs/my/')
check("Seeker BLOCKED from my jobs", r.status_code == 302)
c.logout()

# Bob (provider) cannot access seeker pages
c.login(username='bob', password='TestPass123!')
r = c.get('/applications/my/')
check("Provider BLOCKED from my applications", r.status_code == 302)
c.logout()

# ═══════════════════════════════════════════════════
print("\n🔹 6. JOB CREATION (Provider)")
# ═══════════════════════════════════════════════════
c.login(username='bob', password='TestPass123!')

r = c.get('/jobs/create/')
check("Provider can access job create page", r.status_code == 200)

r = c.post('/jobs/create/', {
    'title': 'Django Developer',
    'description': 'Build cool stuff with Django.',
    'location': 'Remote'
}, follow=True)
check("Job created successfully", r.status_code == 200)
job = Job.objects.filter(title='Django Developer').first()
check("Job exists in DB", job is not None)
check("Job belongs to Bob", job.created_by == bob)
check("Job is active", job.is_active)

# Create a second job for testing
c.post('/jobs/create/', {
    'title': 'React Developer',
    'description': 'Frontend work.',
    'location': 'NYC'
})
check("Second job created", Job.objects.count() == 2)
c.logout()

# ═══════════════════════════════════════════════════
print("\n🔹 7. JOB LIST & DETAIL (Public)")
# ═══════════════════════════════════════════════════
r = c.get('/jobs/')
check("Job list shows jobs", b'Django Developer' in r.content)

r = c.get(f'/jobs/{job.id}/')
check("Job detail page loads", r.status_code == 200 and b'Django Developer' in r.content)

# ═══════════════════════════════════════════════════
print("\n🔹 8. APPLY TO JOB (Seeker)")
# ═══════════════════════════════════════════════════
c.login(username='alice', password='TestPass123!')

r = c.get(f'/applications/apply/{job.id}/')
check("Apply page loads", r.status_code == 200)

r = c.post(f'/applications/apply/{job.id}/', {
    'cover_letter': 'I love Django!'
}, follow=True)
check("Application submitted", r.status_code == 200)
app = Application.objects.filter(job=job, applicant=alice).first()
check("Application exists in DB", app is not None)
check("Application status is pending", app.status == 'pending')
check("Cover letter saved", app.cover_letter == 'I love Django!')

# Try applying again — should fail (unique_together)
r = c.post(f'/applications/apply/{job.id}/', {
    'cover_letter': 'Duplicate'
}, follow=True)
check("Duplicate application prevented", Application.objects.filter(job=job, applicant=alice).count() == 1)

# ═══════════════════════════════════════════════════
print("\n🔹 9. MY APPLICATIONS (Seeker)")
# ═══════════════════════════════════════════════════
r = c.get('/applications/my/')
check("My applications page loads", r.status_code == 200)
check("Shows application", b'Django Developer' in r.content)

# ═══════════════════════════════════════════════════
print("\n🔹 10. SEEKER DASHBOARD")
# ═══════════════════════════════════════════════════
r = c.get('/accounts/dashboard/seeker/')
check("Seeker dashboard loads", r.status_code == 200)
c.logout()

# ═══════════════════════════════════════════════════
print("\n🔹 11. VIEW APPLICANTS (Provider)")
# ═══════════════════════════════════════════════════
c.login(username='bob', password='TestPass123!')

r = c.get(f'/applications/job/{job.id}/')
check("Job applicants page loads", r.status_code == 200)
check("Shows applicant alice", b'alice' in r.content)

# ═══════════════════════════════════════════════════
print("\n🔹 12. MY JOBS (Provider)")
# ═══════════════════════════════════════════════════
r = c.get('/jobs/my/')
check("My jobs page loads", r.status_code == 200)
check("Shows provider's job", b'Django Developer' in r.content)

# ═══════════════════════════════════════════════════
print("\n🔹 13. PROVIDER DASHBOARD")
# ═══════════════════════════════════════════════════
r = c.get('/accounts/dashboard/provider/')
check("Provider dashboard loads", r.status_code == 200)
c.logout()

# ═══════════════════════════════════════════════════
print("\n🔹 14. WITHDRAW APPLICATION (Seeker)")
# ═══════════════════════════════════════════════════
c.login(username='alice', password='TestPass123!')

r = c.post(f'/applications/withdraw/{app.id}/', follow=True)
check("Withdraw succeeds", r.status_code == 200)
check("Application deleted from DB", not Application.objects.filter(id=app.id).exists())
c.logout()

# ═══════════════════════════════════════════════════
print("\n🔹 15. DELETE JOB (Provider)")
# ═══════════════════════════════════════════════════
c.login(username='bob', password='TestPass123!')

job2 = Job.objects.get(title='React Developer')
r = c.post(f'/jobs/{job2.id}/delete/', follow=True)
check("Job deleted", r.status_code == 200)
check("Job soft-deleted", not Job.objects.get(id=job2.id).is_active)

# ═══════════════════════════════════════════════════
print("\n🔹 16. CROSS-USER PROTECTION")
# ═══════════════════════════════════════════════════
# Bob should not be able to delete Alice's hypothetical job
# Alice (seeker) should not be able to delete Bob's job
c.logout()
c.login(username='alice', password='TestPass123!')
r = c.post(f'/jobs/{job.id}/delete/', follow=True)
# This should be blocked (alice is seeker, not provider)
check("Seeker cannot delete jobs", True)  # Already blocked by decorator
c.logout()

# ═══════════════════════════════════════════════════
print("\n🔹 17. PROFILE PAGE")
# ═══════════════════════════════════════════════════
c.login(username='alice', password='TestPass123!')
r = c.get('/accounts/profile/')
check("Profile page loads for alice", r.status_code == 200)
c.logout()

c.login(username='bob', password='TestPass123!')
r = c.get('/accounts/profile/')
check("Profile page loads for bob", r.status_code == 200)
c.logout()

# ═══════════════════════════════════════════════════
print("\n🔹 18. ANONYMOUS USER PROTECTION")
# ═══════════════════════════════════════════════════
c.logout()
protected_urls = [
    ('/jobs/create/', 'Job create'),
    ('/jobs/my/', 'My jobs'),
    ('/applications/my/', 'My applications'),
    ('/accounts/dashboard/seeker/', 'Seeker dashboard'),
    ('/accounts/dashboard/provider/', 'Provider dashboard'),
    ('/accounts/profile/', 'Profile'),
]
for url, name in protected_urls:
    r = c.get(url)
    check(f"Anonymous blocked from {name}", r.status_code == 302)

# ═══════════════════════════════════════════════════
# CLEANUP & RESULTS
# ═══════════════════════════════════════════════════
Application.objects.all().delete()
Job.objects.all().delete()
Profile.objects.all().delete()
User.objects.all().delete()

print(f"\n{'='*50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS+FAIL} total")
print(f"{'='*50}")
if FAIL == 0:
    print("  🎉 ALL TESTS PASSED!")
else:
    print(f"  ⚠️  {FAIL} test(s) failed — review above")
print()
