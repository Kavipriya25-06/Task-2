# time_management\management\commands\trigger_leaves_save.py

from django.core.management.base import BaseCommand
from django.db import transaction
from time_management.models import LeavesTaken


class Command(BaseCommand):
    help = "Triggers save() on all LeavesTaken records to regenerate LeaveDay entries via signal."

    def add_arguments(self, parser):
        parser.add_argument(
            "--approved-only",
            action="store_true",
            help="Only trigger save() for approved leaves (recommended).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate the operation without actually saving.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        approved_only = options["approved_only"]
        dry_run = options["dry_run"]

        if approved_only:
            queryset = LeavesTaken.objects.filter(status="approved")
        else:
            queryset = LeavesTaken.objects.all()

        total = queryset.count()

        if total == 0:
            self.stdout.write(self.style.WARNING("No leave records found."))
            return

        self.stdout.write(
            self.style.NOTICE(
                f"Found {total} LeavesTaken records. {'(Approved only)' if approved_only else '(All statuses)'}"
            )
        )

        processed = 0

        for leave in queryset.iterator():  # iterator() saves memory on large datasets
            processed += 1

            if dry_run:
                self.stdout.write(
                    f"[Dry Run] Would trigger save() for {leave.leave_taken_id} ({leave.employee})"
                )
                continue

            try:
                leave.save(
                    update_fields=["status"]
                )  # Minimal update to trigger post_save
                self.stdout.write(
                    self.style.SUCCESS(
                        f" Processed {processed}/{total}: {leave.leave_taken_id} ({leave.employee})"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f" Error processing {leave.leave_taken_id}: {str(e)}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f"\n Completed processing {processed} leave records.")
        )
