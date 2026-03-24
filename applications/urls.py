from django.urls import path
from . import views

urlpatterns = [
    path("apply/<int:job_id>/", views.apply_to_job, name="apply_to_job"),
    path("withdraw/<int:app_id>/", views.withdraw_application, name="withdraw_application"),
    path("job/<int:job_id>/", views.job_applications, name="job_applications"),
    path("my/", views.my_applications, name="my_applications"),
    path("status/<int:app_id>/", views.update_application_status, name="update_application_status"),
]
