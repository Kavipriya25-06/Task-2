import os
import csv
from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings


class Command(BaseCommand):
    help = "Export all models to CSV files"

    def handle(self, *args, **options):
        export_dir = os.path.join(settings.BASE_DIR, "exports")
        os.makedirs(export_dir, exist_ok=True)

        app_models = apps.get_models()

        for model in app_models:
            model_name = model.__name__
            csv_filename = os.path.join(export_dir, f"{model_name}.csv")

            queryset = model.objects.all()

            if not queryset.exists():
                self.stdout.write(
                    self.style.WARNING(f"Skipping {model_name} (no records)")
                )
                continue

            with open(csv_filename, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                field_names = [field.name for field in model._meta.fields]
                writer.writerow(field_names)

                for obj in queryset:
                    row = [getattr(obj, field) for field in field_names]
                    writer.writerow(row)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Exported {model_name} ({queryset.count()} rows) to {csv_filename}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "✅ All models exported to CSV in the 'exports/' folder."
            )
        )
