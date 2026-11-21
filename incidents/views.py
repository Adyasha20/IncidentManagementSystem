import csv
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import AdminIncidentForm, AgentUpdateForm, AttachmentForm, CommentForm, IncidentForm
from .models import AuditLog, Incident


def _role(user, role):
    if user.role != role:
        raise PermissionDenied


def _log(incident, user, old_status='', new_status='', message=''):
    AuditLog.objects.create(incident=incident, changed_by=user, old_status=old_status, new_status=new_status, message=message)


@login_required
def create_incident(request):
    _role(request.user, 'REPORTER')
    form = IncidentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        incident = form.save(commit=False)
        incident.reported_by = request.user
        incident.save()
        _log(incident, request.user, new_status='OPEN', message='Incident created')
        messages.success(request, 'Incident submitted successfully.')
        return redirect('incident_detail', pk=incident.pk)
    return render(request, 'incidents/create_incident.html', {'form': form})


@login_required
def my_incidents(request):
    _role(request.user, 'REPORTER')
    incidents = filter_incidents(Incident.objects.filter(reported_by=request.user), request).order_by('-created_at')
    return render(request, 'incidents/my_incidents.html', {'incidents': incidents, 'categories': categories(), 'filters': request.GET})


def categories():
    from .models import Category
    return Category.objects.all()


def filter_incidents(queryset, request):
    if q := request.GET.get('q'):
        queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q))
    for field in ('status', 'priority', 'category'):
        if value := request.GET.get(field):
            queryset = queryset.filter(**{field: value})
    return queryset


@login_required
def incident_detail(request, pk):
    incident = get_object_or_404(Incident.objects.select_related('reported_by', 'assigned_to', 'category'), pk=pk)
    user = request.user
    if user.role == 'REPORTER' and incident.reported_by_id != user.id:
        raise PermissionDenied
    if user.role == 'AGENT' and incident.assigned_to_id != user.id:
        raise PermissionDenied
    comment_form = CommentForm(can_make_internal=user.role in ('AGENT', 'ADMIN'))
    attachment_form = AttachmentForm()
    comments = incident.comments.select_related('author')
    if user.role == 'REPORTER':
        comments = comments.filter(internal=False)
    return render(request, 'incidents/incident_detail.html', {'incident': incident, 'comments': comments, 'comment_form': comment_form, 'attachment_form': attachment_form})


@login_required
def edit_incident(request, pk):
    incident = get_object_or_404(Incident, pk=pk, reported_by=request.user)
    _role(request.user, 'REPORTER')
    if incident.status != 'OPEN':
        messages.error(request, 'Only open incidents can be edited.')
        return redirect('incident_detail', pk=pk)
    form = IncidentForm(request.POST or None, instance=incident)
    if request.method == 'POST' and form.is_valid():
        form.save(); _log(incident, request.user, message='Incident details updated')
        messages.success(request, 'Incident updated.')
        return redirect('incident_detail', pk=pk)
    return render(request, 'incidents/incident_form.html', {'form': form, 'heading': 'Edit incident'})


@login_required
def delete_incident(request, pk):
    incident = get_object_or_404(Incident, pk=pk, reported_by=request.user)
    _role(request.user, 'REPORTER')
    if incident.assigned_to_id:
        messages.error(request, 'Assigned incidents cannot be deleted.')
    elif request.method == 'POST':
        incident.delete(); messages.success(request, 'Incident deleted.')
        return redirect('my_incidents')
    return render(request, 'incidents/confirm_delete.html', {'incident': incident})


@login_required
def add_comment(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    if request.method != 'POST': return redirect('incident_detail', pk=pk)
    if request.user.role == 'REPORTER' and incident.reported_by_id != request.user.id: raise PermissionDenied
    if request.user.role == 'AGENT' and incident.assigned_to_id != request.user.id: raise PermissionDenied
    form = CommentForm(request.POST, can_make_internal=request.user.role in ('AGENT', 'ADMIN'))
    if form.is_valid():
        comment = form.save(commit=False); comment.incident = incident; comment.author = request.user; comment.save()
        _log(incident, request.user, message='Comment added')
    return redirect('incident_detail', pk=pk)


@login_required
def add_attachment(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    if request.user.role == 'REPORTER' and incident.reported_by_id != request.user.id: raise PermissionDenied
    if request.user.role == 'AGENT' and incident.assigned_to_id != request.user.id: raise PermissionDenied
    form = AttachmentForm(request.POST, request.FILES)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False); item.incident = incident; item.uploaded_by = request.user; item.save()
    return redirect('incident_detail', pk=pk)


@login_required
def agent_incidents(request):
    _role(request.user, 'AGENT')
    incidents = filter_incidents(Incident.objects.filter(assigned_to=request.user), request).order_by('-updated_at')
    return render(request, 'incidents/agent_incidents.html', {'incidents': incidents, 'categories': categories(), 'filters': request.GET})


@login_required
def agent_update(request, pk):
    _role(request.user, 'AGENT')
    incident = get_object_or_404(Incident, pk=pk, assigned_to=request.user)
    form = AgentUpdateForm(request.POST or None, instance=incident)
    if request.method == 'POST' and form.is_valid():
        old = incident.status; incident = form.save()
        _log(incident, request.user, old, incident.status, 'Agent updated status')
        messages.success(request, 'Status updated.')
        return redirect('incident_detail', pk=pk)
    return render(request, 'incidents/incident_form.html', {'form': form, 'heading': 'Update incident status'})


@login_required
def admin_incidents(request):
    _role(request.user, 'ADMIN')
    incidents = filter_incidents(Incident.objects.select_related('reported_by', 'assigned_to', 'category'), request).order_by('-created_at')
    return render(request, 'incidents/admin_incidents.html', {'incidents': incidents, 'categories': categories(), 'filters': request.GET})


@login_required
def admin_manage_incident(request, pk):
    _role(request.user, 'ADMIN')
    incident = get_object_or_404(Incident, pk=pk)
    form = AdminIncidentForm(request.POST or None, instance=incident)
    if request.method == 'POST' and form.is_valid():
        was_assigned = incident.assigned_to_id; old = incident.status
        incident = form.save(commit=False)
        if incident.assigned_to_id and not was_assigned and incident.status == 'OPEN': incident.status = 'IN_PROGRESS'
        incident.save(); _log(incident, request.user, old, incident.status, 'Administrator updated assignment or SLA')
        messages.success(request, 'Incident updated.')
        return redirect('incident_detail', pk=pk)
    return render(request, 'incidents/incident_form.html', {'form': form, 'heading': 'Manage incident'})


@login_required
def close_incident(request, pk):
    _role(request.user, 'ADMIN')
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == 'POST':
        if incident.status != 'RESOLVED': messages.error(request, 'Only resolved incidents can be closed.')
        else:
            old = incident.status; incident.status = 'CLOSED'; incident.save(); _log(incident, request.user, old, 'CLOSED', 'Administrator closed incident')
            messages.success(request, 'Incident closed.')
    return redirect('incident_detail', pk=pk)


@login_required
def export_csv(request):
    _role(request.user, 'ADMIN')
    response = HttpResponse(content_type='text/csv'); response['Content-Disposition'] = 'attachment; filename="incidents.csv"'
    writer = csv.writer(response); writer.writerow(['ID', 'Title', 'Category', 'Priority', 'Status', 'Reporter', 'Agent', 'Created', 'Deadline'])
    for i in Incident.objects.select_related('category', 'reported_by', 'assigned_to'):
        writer.writerow([i.id, i.title, i.category, i.priority, i.status, i.reported_by, i.assigned_to or '', i.created_at, i.deadline or ''])
    return response
