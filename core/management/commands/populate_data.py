from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile
from jobs.models import Job
from applications.models import Application
from django.db import transaction

class Command(BaseCommand):
    help = 'Populates the database with test seekers, providers, jobs, and applications'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting population...")

        with transaction.atomic():
            pw = "WorkBeeDemo123!"

            providers_data = [
                ("techcorp", "hr@techcorp.com"),
                ("datasystems", "recruiting@datasystems.com"),
                ("innovatellc", "careers@innovatellc.com")
            ]

            seekers_data = [
                ("alice_smith", "alice@example.com"),
                ("bob_jones", "bob@example.com"),
                ("charlie_brown", "charlie@example.com"),
                ("diana_prince", "diana@example.com"),
                ("evan_wright", "evan@example.com"),
                ("frank_castle", "frank@example.com"),
                ("grace_hopper", "grace@example.com"),
                ("hank_pym", "hank@example.com"),
                ("ivy_lee", "ivy@example.com"),
                ("john_doe", "john@example.com")
            ]

            providers = []
            for u, e in providers_data:
                user, _ = User.objects.get_or_create(username=u, email=e)
                user.set_password(pw)
                user.save()
                profile = user.profile
                profile.role = "provider"
                profile.save()
                providers.append(user)

            seekers = []
            for u, e in seekers_data:
                user, _ = User.objects.get_or_create(username=u, email=e)
                user.set_password(pw)
                user.save()
                profile = user.profile
                profile.role = "seeker"
                profile.save()
                seekers.append(user)

            job_titles = ["Software Engineer", "Data Analyst", "UX Designer", "Product Manager", "DevOps Engineer"]
            jobs = []
            for i, p in enumerate(providers):
                for title in job_titles:
                    job, _ = Job.objects.get_or_create(
                        title=f"{title}",
                        description=f"We are looking for a highly skilled {title} to join our team. Remote ok.",
                        location="Remote",
                        created_by=p
                    )
                    jobs.append(job)
            
            # Ensure we start fresh for applications to hit exact counts securely
            Application.objects.all().delete()
            
            app_count = 0
            # 10 seekers apply to 3 jobs each = 30 applications
            for i, s in enumerate(seekers):
                for j in range(3):
                    # Pick a job index that ensures uniqueness per applicant
                    job_index = (i * 3 + j) % len(jobs)
                    job = jobs[job_index]
                    
                    app, created = Application.objects.get_or_create(
                        job=job,
                        applicant=s,
                        defaults={"cover_letter": "I would love to apply for this position and think my skills align perfectly."}
                    )
                    
                    if app_count < 10:
                        app.status = Application.Status.ACCEPTED
                    elif app_count < 20:
                        app.status = Application.Status.REJECTED
                    else:
                        app.status = Application.Status.PENDING
                        
                    app.save()
                    app_count += 1
            
            self.stdout.write(self.style.SUCCESS(f"Successfully created {len(providers)} providers, {len(seekers)} seekers, {len(jobs)} jobs, and {app_count} applications!"))
