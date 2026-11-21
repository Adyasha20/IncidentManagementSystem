# Incident Management System

A Django helpdesk application with Reporter, Agent, and Admin roles. Reporters submit and track incidents; agents work only on assigned tickets; administrators assign work, manage SLAs, and close resolved tickets.

## Included features

- Role-based dashboards and access controls
- Incident submission, search, filters, edit/delete rules, and detail pages
- Admin assignment, priority/category/deadline management, closure, and CSV export
- Agent assigned-work queue and status updates
- Comments (including agent/admin internal notes), file attachments, and an audit timeline
- SLA overdue indicator and dashboard metrics

## Run locally

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Create users in Django admin and set each user's `role` to `REPORTER`, `AGENT`, or `ADMIN`.

## Deployment

Set `DEBUG=False`, `SECRET_KEY`, and `ALLOWED_HOSTS` in your hosting environment. For Render, install from `requirements.txt`, run `python manage.py migrate && python manage.py collectstatic --noinput`, and use `gunicorn config.wsgi` as the start command. Set a PostgreSQL `DATABASE_URL` and add `dj-database-url` if moving off SQLite.
