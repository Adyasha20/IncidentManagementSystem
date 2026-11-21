from .decorators import role_required
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
from django.utils import timezone
from incidents.models import Incident

@login_required
@role_required("REPORTER")
def reporter_dashboard(request):
    incidents = Incident.objects.filter(reported_by=request.user)
    return render(request, "dashboards/reporter_dashboard.html", {'open_count': incidents.filter(status='OPEN').count(), 'progress_count': incidents.filter(status='IN_PROGRESS').count(), 'resolved_count': incidents.filter(status__in=['RESOLVED', 'CLOSED']).count(), 'recent': incidents.order_by('-created_at')[:5]})


@login_required
@role_required("AGENT")
def agent_dashboard(request):
    incidents = Incident.objects.filter(assigned_to=request.user)
    return render(request, "dashboards/agent_dashboard.html", {'assigned_count': incidents.exclude(status__in=['RESOLVED', 'CLOSED']).count(), 'overdue_count': sum(i.is_overdue for i in incidents), 'resolved_count': incidents.filter(status='RESOLVED').count(), 'recent': incidents.order_by('-updated_at')[:5]})


@login_required
@role_required("ADMIN")
def admin_dashboard(request):
    incidents = Incident.objects.all()
    context = {
        'total': incidents.count(), 'open_count': incidents.filter(status='OPEN').count(), 'progress_count': incidents.filter(status='IN_PROGRESS').count(), 'resolved_count': incidents.filter(status='RESOLVED').count(), 'closed_count': incidents.filter(status='CLOSED').count(),
        'recent': incidents.select_related('category', 'reported_by').order_by('-created_at')[:8],
        'category_stats': incidents.values('category__name').annotate(total=Count('id')).order_by('-total'),
        'agent_stats': incidents.filter(assigned_to__isnull=False).values('assigned_to__username').annotate(total=Count('id')).order_by('-total'),
    }
    return render(request, "dashboards/admin_dashboard.html", context)


@login_required
def redirect_dashboard(request):

    if request.user.role == "REPORTER":
        return redirect("reporter_dashboard")

    elif request.user.role == "AGENT":
        return redirect("agent_dashboard")

    elif request.user.role == "ADMIN":
        return redirect("admin_dashboard")

    return redirect("home")


from django.contrib.auth import login
from .forms import RegisterForm

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('dashboard_redirect')
    return render(request, 'registration/register.html', {'form': form})
