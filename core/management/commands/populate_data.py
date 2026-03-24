"""
Populate database with sample data for WorkBee demo.
Usage: python manage.py populate_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile
from jobs.models import Job, SavedJob
from applications.models import Application

User = get_user_model()

JOBS_DATA = [
    {
        "title": "Senior Python Developer",
        "description": "We are looking for a Senior Python Developer to join our backend team. You will work on building scalable APIs, designing database schemas, and mentoring junior developers. Experience with Django, PostgreSQL, and Docker is a plus.",
        "location": "San Francisco, CA",
    },
    {
        "title": "Full Stack Engineer",
        "description": "Join our product team as a Full Stack Engineer! You'll build end-to-end features using React and Django. We value clean code and great user experiences.",
        "location": "New York, NY",
    },
    {
        "title": "DevOps Engineer",
        "description": "We need a DevOps Engineer to streamline our CI/CD pipelines, manage AWS infrastructure, and improve deployment workflows. You should have experience with Terraform, Kubernetes, and GitHub Actions.",
        "location": "Remote",
    },
    {
        "title": "UI/UX Designer",
        "description": "We are hiring a creative UI/UX Designer to design beautiful, user-centered interfaces for our web and mobile applications. Figma proficiency and a strong portfolio are required.",
        "location": "Austin, TX",
    },
    {
        "title": "Data Scientist",
        "description": "Looking for a Data Scientist who can analyze large datasets and build predictive models. Proficiency in Python, Pandas, Scikit-learn, and SQL is expected. Experience with NLP is a bonus.",
        "location": "Seattle, WA",
    },
    {
        "title": "Mobile App Developer (React Native)",
        "description": "Build cross-platform mobile applications using React Native. You should have experience publishing to both App Store and Google Play. Familiarity with TypeScript is preferred.",
        "location": "Los Angeles, CA",
    },
    {
        "title": "Backend Engineer (Node.js)",
        "description": "Join a fast-growing startup as a Backend Engineer. You will design microservices, manage databases, and build RESTful APIs using Node.js and Express.",
        "location": "Chicago, IL",
    },
    {
        "title": "Machine Learning Engineer",
        "description": "We are seeking an ML Engineer to build and deploy machine learning models at scale. Deep experience with TensorFlow/PyTorch and MLOps tools is required.",
        "location": "Boston, MA",
    },
    {
        "title": "Technical Writer",
        "description": "Create clear, comprehensive documentation for our developer-facing APIs and SDKs. You should have a strong technical background and excellent writing skills.",
        "location": "Remote",
    },
    {
        "title": "Cybersecurity Analyst",
        "description": "Help protect our systems from threats. You'll conduct vulnerability assessments, monitor security incidents, and implement security protocols across the organization.",
        "location": "Washington, DC",
    },
]


class Command(BaseCommand):
    help = "Populate database with sample WorkBee data"

    def handle(self, *args, **options):
        self.stdout.write("🐝 Populating WorkBee database...\n")

        # --- Create Provider accounts ---
        providers = []
        provider_data = [
            ("techcorp", "techcorp@workbee.com", "TechCorp Inc."),
            ("startupx", "hire@startupx.com", "StartupX"),
            ("bigdata_co", "jobs@bigdata.co", "BigData Co"),
        ]

        for username, email, _ in provider_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email},
            )
            if created:
                user.set_password("password123")
                user.save()
                Profile.objects.update_or_create(user=user, defaults={"role": "provider"})
                self.stdout.write(f"  ✅ Created provider: {username}")
            else:
                self.stdout.write(f"  ⏭  Provider exists: {username}")
            providers.append(user)

        # --- Create Seeker accounts ---
        seekers = []
        seeker_data = [
            ("alice", "alice@example.com"),
            ("bob", "bob@example.com"),
            ("carol", "carol@example.com"),
        ]

        for username, email in seeker_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email},
            )
            if created:
                user.set_password("password123")
                user.save()
                Profile.objects.update_or_create(user=user, defaults={"role": "seeker"})
                self.stdout.write(f"  ✅ Created seeker: {username}")
            else:
                self.stdout.write(f"  ⏭  Seeker exists: {username}")
            seekers.append(user)

        # --- Create Jobs ---
        jobs = []
        for i, job_info in enumerate(JOBS_DATA):
            provider = providers[i % len(providers)]
            job, created = Job.objects.get_or_create(
                title=job_info["title"],
                created_by=provider,
                defaults={
                    "description": job_info["description"],
                    "location": job_info["location"],
                },
            )
            if created:
                self.stdout.write(f"  ✅ Created job: {job.title}")
            else:
                self.stdout.write(f"  ⏭  Job exists: {job.title}")
            jobs.append(job)

        # --- Create Applications ---
        app_scenarios = [
            # (seeker_index, job_index, status)
            (0, 0, "accepted"),
            (0, 1, "pending"),
            (0, 3, "rejected"),
            (0, 5, "pending"),
            (1, 0, "pending"),
            (1, 2, "accepted"),
            (1, 4, "pending"),
            (2, 1, "pending"),
            (2, 6, "rejected"),
            (2, 7, "accepted"),
        ]

        for seeker_idx, job_idx, status in app_scenarios:
            app, created = Application.objects.get_or_create(
                job=jobs[job_idx],
                applicant=seekers[seeker_idx],
                defaults={
                    "cover_letter": f"I am very interested in the {jobs[job_idx].title} position. My skills and experience make me a strong candidate.",
                    "status": status,
                },
            )
            if created:
                self.stdout.write(f"  ✅ Application: {seekers[seeker_idx].username} → {jobs[job_idx].title} [{status}]")

        # --- Create Saved Jobs ---
        save_scenarios = [
            (0, 2), (0, 4), (0, 7),
            (1, 1), (1, 5), (1, 8),
            (2, 0), (2, 3), (2, 9),
        ]

        for seeker_idx, job_idx in save_scenarios:
            _, created = SavedJob.objects.get_or_create(
                job=jobs[job_idx],
                user=seekers[seeker_idx],
            )
            if created:
                self.stdout.write(f"  ✅ Saved: {seekers[seeker_idx].username} ★ {jobs[job_idx].title}")

        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Done! Created {len(providers)} providers, {len(seekers)} seekers, "
            f"{len(jobs)} jobs, {len(app_scenarios)} applications, {len(save_scenarios)} saved jobs."
        ))
        self.stdout.write(self.style.WARNING(
            "\n🔑 All accounts use password: password123"
        ))
