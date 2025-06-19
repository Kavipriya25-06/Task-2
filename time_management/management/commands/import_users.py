import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from time_management.models import User, Employee


class Command(BaseCommand):
    help = "Import users from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to the CSV file")

    def handle(self, *args, **kwargs):
        csv_path = kwargs["csv_path"]

        try:
            with open(csv_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                success_count = 0
                failure_count = 0

                for row in reader:
                    try:
                        with transaction.atomic():
                            emp = None
                            if row.get("employee_id"):
                                emp = Employee.objects.filter(
                                    employee_id=row["employee_id"]
                                ).first()

                            user = User(
                                email=row["email"],
                                password=row["password"],  # Will be hashed in save()
                                role=row.get("role", "employee"),
                                employee_id=emp,
                                status=row.get("status", "active"),
                            )
                            user.save()
                            success_count += 1

                    except Exception as e:
                        self.stderr.write(f"❌ Error processing row {row}: {e}")
                        failure_count += 1

                self.stdout.write(
                    self.style.SUCCESS(f"✅ Imported {success_count} users")
                )
                if failure_count:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️ Skipped {failure_count} rows due to errors"
                        )
                    )

        except FileNotFoundError:
            self.stderr.write(f"❌ File not found: {csv_path}")
