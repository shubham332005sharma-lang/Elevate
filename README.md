# Project Elevate

Elevate is a Django-based elevator incident reporting and management project. The first working slice lets a visitor report an issue, stores it in SQLite, and lets authenticated staff review and update its status.

## Current scope

- Public incident reporting for elevators configured by staff.
- Administrator and Technician roles, with role-aware staff pages.
- Staff incident register, detail, filtering, status, severity, and assignment workflows.
- Incident severity, status, and technician assignment fields.
- Django admin for managing elevators, incidents, and staff accounts.
- SQLite for local development. The hardware and live sensor connection are not connected yet.

## Run locally

Python 3.10+ and the dependencies in `requirements.txt` are required. A virtual environment is optional; it helps keep this project's packages separate from other Python projects.

```powershell
python -m pip install -r requirements.txt
cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py setup_roles
python manage.py runserver 127.0.0.1:8010
```

Open `http://127.0.0.1:8010/`. The app opens the staff login page; opening the root address clears any remembered login so the user must sign in again. Public visitors can choose **Report an issue** without signing in. After creating a superuser and running `setup_roles`, that superuser has the Administrator role and the command creates a Technician demo account with a one-time password printed in the terminal. Add at least one Elevator in Django admin before submitting a report. Administrators manage incidents at `/staff/incidents/` after signing in.

## Roles

| Role | Access |
| --- | --- |
| Administrator | Dashboard, elevator and incident management, Django admin, and user management. |
| Technician | Assigned tasks only, task details for their assigned incidents, and status updates on those tasks. |
| Reporter | Public actor, not a staff login. Can submit an issue from the login page's **Report an issue** link. |

## Template organization

- `backend/incidents/templates/incidents/public/`: login and public reporting pages.
- `backend/incidents/templates/incidents/administrator/`: administrator dashboard, elevator list, and incident register.
- `backend/incidents/templates/incidents/technician/`: technician's assigned-task dashboard.
- `backend/incidents/templates/incidents/shared/`: shared page layout, incident detail, and password pages.
- `backend/incidents/static/incidents/`: CSS and browser-side assets; templates do not store static files.

## Next implementation steps

1. Confirm the incident fields and workflow against the project requirements.
2. Connect ESP32 telemetry and live elevator status to the operational dashboard.
3. Connect ESP32 telemetry after the web workflow is stable.
4. Add the project diagrams, test plan, and user documentation from the implemented behavior.
