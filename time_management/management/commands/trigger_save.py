from django.core.management.base import BaseCommand
from time_management.models import (
    Employee,
    User,
    Hierarchy,
    LeavesAvailable,
)  # Adjust `your_app` to your actual app name
from django.db import transaction


class Command(BaseCommand):
    help = "Triggers save() for all Employees model instances."

    def handle(self, *args, **kwargs):
        total = LeavesAvailable.objects.count()
        self.stdout.write(f"Found {total} Employees. Re-saving each...")

        try:
            with transaction.atomic():
                for emp in LeavesAvailable.objects.iterator():
                    emp.save()
            self.stdout.write(
                self.style.SUCCESS(f"Successfully re-saved all {total} Employees.")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error while saving Employees: {str(e)}")
            )
