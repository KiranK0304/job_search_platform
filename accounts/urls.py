from django.urls import path
from . import views

urlpatterns = [
    # Registration flow
    path("register/", views.choose_role, name="register"),
    path("register/seeker/", views.register_seeker, name="register_seeker"),
    path("register/provider/", views.register_provider, name="register_provider"),

    # Auth
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Profile
    path("profile/", views.profile_view, name="profile"),

    # Dashboards
    path("dashboard/seeker/", views.seeker_dashboard, name="seeker_dashboard"),
    path("dashboard/provider/", views.provider_dashboard, name="provider_dashboard"),
]
