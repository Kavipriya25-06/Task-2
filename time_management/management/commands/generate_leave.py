from django.core.management.base import BaseCommand
from django.utils import timezone
from time_management.models import Employee, LeavesAvailable  # adjust import
from time_management.management.commands.utils import calculate_leave_entitlement  # if separated


class Command(BaseCommand):
    help = "Create LeavesAvailable for all employees with interval-based pro-rata leave"

    def handle(self, *args, **kwargs):
        created_count = 0
        today = timezone.now().date()

        for emp in Employee.objects.all():
            if LeavesAvailable.objects.filter(employee=emp).exists():
                continue

            join_date = emp.doj
            if not join_date:
                continue

            leave_count = calculate_leave_entitlement(join_date)

            LeavesAvailable.objects.create(
                employee=emp,
                sick_leave=leave_count,
                casual_leave=leave_count,
                comp_off=leave_count,
                earned_leave=leave_count,
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"{created_count} leave records created."))
