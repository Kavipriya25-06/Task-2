from django.core.management.base import BaseCommand
from time_management.models import (
    AreaOfWork,
    Roles,
    Discipline,
)  # adjust if models are in another app


class Command(BaseCommand):
    help = "Load static Area of Work and Roles data"

    def handle(self, *args, **kwargs):
        area_of_work_list = [
            ("autospool_extraction", "AutoSpool extraction"),
            ("back_drafting", "Back Drafting"),
            ("caeser_II", "Caeser II"),
            ("checking", "Checking"),
            ("connection_design", "Connection Design"),
            ("coordination", "Coordination"),
            ("ceputation_to_ISGEC", "Deputation to ISGEC"),
            ("detailing", "Detailing"),
            ("documentation", "Documentation"),
            ("drawing_preparation", "Drawing Preparation"),
            ("drawings_preparation", "Drawings Preparation"),
            ("estimation", "Estimation"),
            ("hydro_test_pack_preparation", "Hydro test pack Preparation"),
            ("meeting", "Meeting"),
            ("model_correction", "Model Correction"),
            ("modeling", "Modeling"),
            ("preliminary_ga", "Preliminary GA"),
            ("preliminary_modeling", "Preliminary Modeling"),
            ("primary_design", "Primary Design"),
            ("qc", "QC"),
            ("review", "Review"),
            ("second_level_checking", "Second Level Checking"),
            ("stress_analysis", "Stress Analysis"),
            ("training", "Training"),
        ]

        discipline_list = [
            (
                99,
                "Non Billable Projects/Hours",
            ),
            (
                0,
                "Proposals",
            ),
            (
                1,
                "Standardization",
            ),
            (
                2,
                "Deputation",
            ),
            (
                51,
                "Structural - Detailing",
            ),
            (
                52,
                "Structural - Design  + Detailing",
            ),
            (
                53,
                "Structural - Design",
            ),
            (
                54,
                "Piping Design",
            ),
            (
                55,
                "Piping Detailing",
            ),
            (
                56,
                "Mechanical Design",
            ),
            (
                57,
                "Mechanical Detailing",
            ),
            (
                58,
                "EIC",
            ),
            (
                59,
                "Multidiscipline",
            ),
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
            obj, created = AreaOfWork.objects.get_or_create(
                area_name=name[0], name=name[1]
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added AreaOfWork: {name}"))

        # Load Discipline
        for name in discipline_list:
            obj, created = Discipline.objects.get_or_create(
                discipline_code=name[0], name=name[1]
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added Discipline: {name}"))

        # Load Roles
        for role in roles_list:
            obj, created = Roles.objects.get_or_create(role=role)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added Role: {role}"))

        self.stdout.write(self.style.SUCCESS("Static data load complete ✅"))
