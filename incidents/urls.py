from django.urls import path
from . import views

urlpatterns = [
    path(
        "create/",
        views.create_incident,
        name="create_incident",
    ),

    path(
        "my/",
        views.my_incidents,
        name="my_incidents",
    ),
    path('<int:pk>/', views.incident_detail, name='incident_detail'),
    path('<int:pk>/edit/', views.edit_incident, name='edit_incident'),
    path('<int:pk>/delete/', views.delete_incident, name='delete_incident'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('<int:pk>/attachment/', views.add_attachment, name='add_attachment'),
    path('agent/assigned/', views.agent_incidents, name='agent_incidents'),
    path('agent/<int:pk>/update/', views.agent_update, name='agent_update'),
    path('admin/all/', views.admin_incidents, name='admin_incidents'),
    path('admin/<int:pk>/manage/', views.admin_manage_incident, name='admin_manage_incident'),
    path('admin/<int:pk>/close/', views.close_incident, name='close_incident'),
    path('admin/export/', views.export_csv, name='export_csv'),
]
