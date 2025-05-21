from datetime import date
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from time_management.models import Employee, LeavesAvailable  # adjust import
from time_management.management.commands.utils import (
    calculate_leave_entitlement,
)  # if separated


class Command(BaseCommand):
    help = "Create LeavesAvailable for all employees with interval-based pro-rata leave"

    def handle(self, *args, **kwargs):
        created_count = 0
        today = timezone.now().date()

        for emp in Employee.objects.all():
            if LeavesAvailable.objects.filter(employee=emp).exists():
                continue

            join_date = emp.doj
            if not join_date or not emp.employment_type:
                continue

            # Determine effective employment type
            effective_type = emp.employment_type
            if (
                emp.employment_type == "Probation"
                and emp.probation_confirmation_date
                and today >= emp.probation_confirmation_date
            ):
                effective_type = "Fulltime"
                join_date = (
                    emp.probation_confirmation_date
                )  # start fulltime benefit from confirmation

            sick_leave = casual_leave = earned_leave = comp_off = 0

            if effective_type == "Fulltime":
                leave_count = calculate_leave_entitlement(join_date)
                sick_leave = casual_leave = earned_leave = leave_count

            elif effective_type == "Probation":
                end_date = emp.probation_confirmation_date
                if end_date:
                    months = max(
                        (end_date.year - join_date.year) * 12
                        + end_date.month
                        - join_date.month,
                        1,
                    )
                    casual_leave = months  # 1 per month

            elif effective_type == "Contract":
                end_date = emp.contract_end_date
                if end_date:
                    months = max(
                        (end_date.year - join_date.year) * 12
                        + end_date.month
                        - join_date.month,
                        1,
                    )
                    casual_leave = months  # 1 per month

            elif effective_type == "Internship":
                pass  # No leave for interns

            # leave_count = calculate_leave_entitlement(join_date)

            LeavesAvailable.objects.create(
                employee=emp,
                sick_leave=sick_leave,
                casual_leave=casual_leave,
                comp_off=comp_off,
                earned_leave=earned_leave,
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"{created_count} leave records created."))
