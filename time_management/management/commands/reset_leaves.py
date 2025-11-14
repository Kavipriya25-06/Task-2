from django.core.management.base import BaseCommand
from django.utils import timezone
from time_management.models import (
    LeavesAvailable,
    LeaveOpeningBalance,
    Employee,
    MonthlyLeaveBalance,
)  # Adjust this import path to your app
from datetime import datetime
from decimal import Decimal
from django.db import transaction

from time_management.signals import rebuild_monthly_balances


FULLTIME_DEFAULTS = {
    "sick": Decimal("6.0"),
    "casual": Decimal("12.0"),
    "earned": Decimal("6.0"),
}

NONFULLTIME_DEFAULTS = {
    "sick": Decimal("0.0"),
    "casual": Decimal("0.0"),
    "earned": Decimal("0.0"),
}


def policy_entitlements_for(employee: Employee) -> dict:
    """Return policy reset for SL/CL/EL (NOT including comp-off carry)."""
    if getattr(employee, "employment_type", "") == "Fulltime":
        return FULLTIME_DEFAULTS.copy()
    return NONFULLTIME_DEFAULTS.copy()


def get_comp_off_carry_forward(employee: Employee, prev_year: int) -> Decimal:
    """
    Carry forward ONLY Comp-Off from previous year December closing.
    If the Dec record is missing, try rebuilding the previous year's chain first.
    """
    dec_row = MonthlyLeaveBalance.objects.filter(
        employee=employee, year=prev_year, month=12
    ).first()

    if dec_row is None:
        # Rebuild previous year to materialize Dec closing
        rebuild_monthly_balances(employee_id=employee.pk, year=prev_year, start_month=1)
        dec_row = MonthlyLeaveBalance.objects.filter(
            employee=employee, year=prev_year, month=12
        ).first()

    return getattr(dec_row, "comp_off_balance", Decimal("0.0")) or Decimal("0.0")


class Command(BaseCommand):
    help = "Jan 1 rollover: carry forward ONLY Comp-Off; reset SL/CL/EL to policy; upsert LeaveOpeningBalance; rebuild this year's monthly balances."

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        current_year = today.year
        prev_year = current_year - 1

        # If you want to restrict execution to Jan 1 only, uncomment:
        # if not (today.month == 1 and today.day == 1):
        #     self.stdout.write(self.style.WARNING("Intended to run on January 1st."))
        #     return

        count = 0

        # You can switch to Employee.objects.all() if you don't rely on existing LeavesAvailable.
        employees = Employee.objects.all().iterator()

        for emp in employees:
            with transaction.atomic():
                policy = policy_entitlements_for(emp)
                comp_cf = get_comp_off_carry_forward(emp, prev_year)

                # 1) Snapshot: LeavesAvailable reflects the NEW opening
                leaves_avail, _ = LeavesAvailable.objects.get_or_create(employee=emp)
                leaves_avail.sick_leave = policy["sick"]
                leaves_avail.casual_leave = policy["casual"]
                leaves_avail.earned_leave = policy["earned"]
                leaves_avail.comp_off = comp_cf
                leaves_avail.save(
                    update_fields=[
                        "sick_leave",
                        "casual_leave",
                        "earned_leave",
                        "comp_off",
                    ]
                )

                # 2) Upsert: LeaveOpeningBalance for current_year
                lob, created = LeaveOpeningBalance.objects.get_or_create(
                    employee=emp,
                    year=current_year,
                    defaults=dict(
                        sick_leave_opening=policy["sick"],
                        casual_leave_opening=policy["casual"],
                        earned_leave_opening=policy["earned"],
                        comp_off_opening=comp_cf,
                    ),
                )
                if not created:
                    lob.sick_leave_opening = policy["sick"]
                    lob.casual_leave_opening = policy["casual"]
                    lob.earned_leave_opening = policy["earned"]
                    lob.comp_off_opening = comp_cf
                    lob.save(
                        update_fields=[
                            "sick_leave_opening",
                            "casual_leave_opening",
                            "earned_leave_opening",
                            "comp_off_opening",
                        ]
                    )

                # 3) Rebuild this year's monthly balances (Jan→Dec)
                rebuild_monthly_balances(
                    employee_id=emp.pk, year=current_year, start_month=1
                )

                count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Rollover complete for {count} employee(s). "
                f"SL/CL/EL reset per policy, Comp-Off carried from {prev_year} Dec closing."
            )
        )


# class Command(BaseCommand):
#     help = "Reset leaves for all employees annually on Jan 1st"

#     def handle(self, *args, **kwargs):
#         today = timezone.now().date()

#         if today.month == 1 and today.day == 1:
#             leaves = LeavesAvailable.objects.all()
#             for leave in leaves:
#                 emp = leave.employee
#                 print("employee type", emp.employment_type)
#                 if emp and emp.employment_type == "Fulltime":
#                     leave.sick_leave = 6
#                     leave.casual_leave = 12
#                     # leave.comp_off = 0
#                     # leave.earned_leave = 6  # carry forward + new
#                     leave.save()
#             self.stdout.write(
#                 self.style.SUCCESS(" Annual leave reset completed successfully.")
#             )
#         else:
#             self.stdout.write(" This script should only run on January 1st.")
