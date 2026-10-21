# Project Elevate

Elevate is a Django-based elevator incident reporting and management project. The first working slice lets a visitor report an issue, stores it in SQLite, and lets authenticated staff review and update its status.

## Current scope

- Public incident reporting for elevators configured by staff.
- Staff incident list and detail pages, protected by Django login.
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
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. Sign in to `/admin/` with the superuser account, add at least one Elevator, then submit an issue using **Report an issue**. Staff can review incidents at `/staff/incidents/` after signing in.

## Next implementation steps

1. Confirm the incident fields and workflow against the project requirements.
2. Build the operational dashboard and technician-facing views on top of the saved records.
3. Connect ESP32 telemetry after the web workflow is stable.
4. Add the project diagrams, test plan, and user documentation from the implemented behavior.
