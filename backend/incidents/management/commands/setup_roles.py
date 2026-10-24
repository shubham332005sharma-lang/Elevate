import secrets

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the Elevate Administrator and Technician roles and a demo technician account."

    def handle(self, *args, **options):
        administrator, _ = Group.objects.get_or_create(name="Administrator")
        technician, _ = Group.objects.get_or_create(name="Technician")
        reporter, _ = Group.objects.get_or_create(name="Reporter")
        reporter.permissions.clear()

        role_permissions = {
            administrator: ["incidents.elevator", "incidents.incident", "auth.user"],
            technician: ["incidents.elevator", "incidents.incident"],
        }
        for group, models in role_permissions.items():
            permissions = Permission.objects.filter(
                content_type__app_label__in={model.split(".")[0] for model in models},
                content_type__model__in={model.split(".")[1] for model in models},
            )
            if group == technician:
                permissions = permissions.filter(codename__in={
                    "view_elevator", "view_incident", "change_incident"
                })
            group.permissions.set(permissions)

        User = get_user_model()
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            admin.groups.add(administrator)
        if not admins.exists():
            self.stdout.write(self.style.WARNING(
                "No superuser exists yet. Create one with createsuperuser, then rerun setup_roles."
            ))

        technician_user, created = User.objects.get_or_create(
            username="technician",
            defaults={"is_staff": False, "is_active": True},
        )
        technician_user.groups.add(technician)
        if created:
            temporary_password = secrets.token_urlsafe(15)
            technician_user.set_password(temporary_password)
            technician_user.save(update_fields=["password"])
            self.stdout.write(self.style.SUCCESS("Created demo technician account."))
            self.stdout.write(f"Username: {technician_user.username}")
            self.stdout.write(f"Temporary password: {temporary_password}")
            self.stdout.write("Change this password after the first login.")
        else:
            self.stdout.write("Technician account already exists; its password was left unchanged.")

        self.stdout.write(self.style.SUCCESS(
            f"Roles ready: Administrator ({admins.count()} superuser(s) assigned), Technician (1 demo account), Reporter (public submissions, no account)."
        ))
