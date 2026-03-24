from django.urls import path
from . import views

urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("my/", views.my_jobs, name="my_jobs"),
    path("saved/", views.saved_jobs, name="saved_jobs"),
    path("create/", views.job_create, name="job_create"),
    path("<int:job_id>/", views.job_detail, name="job_detail"),
    path("<int:job_id>/delete/", views.job_delete, name="job_delete"),
    path("<int:job_id>/save/", views.save_job, name="save_job"),
]
