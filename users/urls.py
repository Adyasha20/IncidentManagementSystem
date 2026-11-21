from django.urls import path
from . import views

urlpatterns = [

    path(
        "dashboard/",
        views.redirect_dashboard,
        name="dashboard_redirect",
    ),

    path(
        "reporter/dashboard/",
        views.reporter_dashboard,
        name="reporter_dashboard",
    ),

    path(
        "agent/dashboard/",
        views.agent_dashboard,
        name="agent_dashboard",
    ),

    path(
        "admin/dashboard/",
        views.admin_dashboard,
        name="admin_dashboard",
    ),

]
from .views import register
urlpatterns += [path('register/', register, name='register')]
