from django.core.management.base import BaseCommand
from time_management.models import (
    AreaOfWork,
    Roles,
)  # adjust if models are in another app


class Command(BaseCommand):
    help = "Load static Area of Work and Roles data"

    def handle(self, *args, **kwargs):
        area_of_work_list = [
            "AutoSpool extraction",
            "Back Drafting",
            "Caeser II",
            "Checking",
            "Connection Design",
            "Coordination",
            "Deputation to ISGEC",
            "Detailing",
            "Documentation",
            "Drawing Preparation",
            "Drawings Preparation",
            "Estimation",
            "Hydro test pack Preparation",
            "Meeting",
            "Model Correction",
            "Modeling",
            "Preliminary GA",
            "Preliminary Modeling",
            "Primary Design",
            "QC",
            "Review",
            "Second Level Checking",
            "Stress Analysis",
            "Training",
        ]

        roles_list = [
            "admin",
            "employee",
            "hr",
            "manager",
            "teamlead",
        ]

        # Load AreaOfWork
        for name in area_of_work_list:
            obj, created = AreaOfWork.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added AreaOfWork: {name}"))

        # Load Roles
        for role in roles_list:
            obj, created = Roles.objects.get_or_create(role=role)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added Role: {role}"))

        self.stdout.write(self.style.SUCCESS("Static data load complete ✅"))
