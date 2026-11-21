from django.contrib import admin
from .models import Attachment, AuditLog, Category, Comment, Incident

admin.site.register(Category)
@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'reported_by', 'assigned_to', 'deadline')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description')

admin.site.register([Comment, AuditLog, Attachment])
