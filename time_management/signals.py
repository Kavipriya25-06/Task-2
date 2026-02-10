from django.db.models.signals import post_save, post_delete, pre_save, pre_delete

from decimal import Decimal
from django.db import transaction
from django.db.models.functions import ExtractYear, ExtractMonth, Coalesce
from collections import defaultdict
from django.dispatch import receiver
from django.core.mail import send_mail
from django.db.models import Sum, Q
from datetime import timedelta, date
from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone
from .models import (
    Employee,
    LeavesAvailable,
    Hierarchy,
    User,
    Variation,
    TimeSheet,
    LeavesTaken,
    Project,
    Calendar,
    TaskAssign,
    LeaveDay,
    MonthlyLeaveAvailed,
    LeaveOpeningBalance,
    MonthlyLeaveBalance,
    CompOffRequest,
)
from time_management.management.commands.utils import (
    calculate_leave_entitlement,
    create_or_update_leaves_for_employee,
)  # create this in utils.py


# @receiver(post_save, sender=Employee)
# def create_leave_record(sender, instance, created, **kwargs):
#     """
#     - Create leave record if it doesn't exist

#     """

#     if created:
#         created = create_or_update_leaves_for_employee(instance)
# if created and not LeavesAvailable.objects.filter(employee=instance).exists():
#     if instance.doj:
#         leave_count = calculate_leave_entitlement(instance.doj)
#     else:
#         leave_count = 0

#     LeavesAvailable.objects.create(
#         employee=instance,
#         sick_leave=leave_count,
#         casual_leave=leave_count,
#         comp_off=0,
#         earned_leave=leave_count,
#     )

# LEAVE_PROJECT_MAP = {
#     "casual_leave": "99002",  # Casual Leave
#     "sick_leave": "99003",  # Sick Leave
#     "earned_leave": "99004",  # Earned Leave
#     "comp_off": "99004a",  # Comp Off
#     "lop": "99006",  # Loss of Pay (if needed)
# }


# @receiver(post_save, sender=LeavesTaken)
# def update_leave_project_consumed_hours(sender, instance, created, **kwargs):
#     leave_type_key = instance.leave_type.strip().lower()
#     project_code = LEAVE_PROJECT_MAP.get(leave_type_key)

#     if created and project_code:
#         try:
#             project = Project.objects.get(project_code=project_code)
#             increment = (instance.duration or 0) * 8
#             project.consumed_hours = (project.consumed_hours or 0) + increment
#             project.save()
#         except Project.DoesNotExist:
#             pass


# @receiver(post_delete, sender=LeavesTaken)
# def rollback_leave_project_consumed_hours(sender, instance, **kwargs):
#     leave_type_key = instance.leave_type.strip().lower()
#     project_code = LEAVE_PROJECT_MAP.get(leave_type_key)

#     if project_code:
#         try:
#             project = Project.objects.get(project_code=project_code)
#             decrement = (instance.duration or 0) * 8
#             project.consumed_hours = max(0, (project.consumed_hours or 0) - decrement)
#             project.save()
#         except Project.DoesNotExist:
#             pass


# HOLIDAY_PROJECT_CODE = "99009"


# @receiver([post_save, post_delete], sender=Calendar)
# def update_consumed_hours_for_holidays(sender, instance, **kwargs):
#     """
#     Recalculates holiday project consumed_hours as:
#     Sum over all holidays (8 hours x number of employees active on that day).
#     """
#     try:
#         holidays = Calendar.objects.filter(is_holiday=True)
#         total_hours = 0

#         for holiday in holidays:
#             holiday_date = holiday.date
#             # Get employees who were active on that day (joined on or before that day and not yet relieved)
#             active_employees = Employee.objects.filter(
#                 Q(doj__lte=holiday_date),
#                 Q(relieving_date__isnull=True) | Q(relieving_date__gte=holiday_date),
#                 status="active",
#             ).count()

#             total_hours += active_employees * 8

#         project = Project.objects.get(project_code=HOLIDAY_PROJECT_CODE)
#         project.consumed_hours = total_hours
#         project.save()

#     except Project.DoesNotExist:
#         pass  # Optionally log


HOLIDAY_TASK_ASSIGN_ID = "TKASS_01011"


@receiver([post_save, post_delete], sender=Calendar)
def update_timesheets_for_holiday_calendar_change(sender, instance, **kwargs):

    holiday_date = instance.date
    if not instance.is_holiday:
        # Clean up any holiday timesheets on this date
        TimeSheet.objects.filter(
            date=instance.date, task_assign__task_assign_id=HOLIDAY_TASK_ASSIGN_ID
        ).delete()
        return

    # If it's not a holiday anymore or if the date is in the future, skip creating
    if not instance.is_holiday or holiday_date > date.today():
        return

    try:
        task_assign = TaskAssign.objects.get(task_assign_id=HOLIDAY_TASK_ASSIGN_ID)
    except TaskAssign.DoesNotExist:
        print(f"[WARN] TaskAssign {HOLIDAY_TASK_ASSIGN_ID} not found.")
        return

    # Clean up any stale timesheets before creating fresh ones
    TimeSheet.objects.filter(date=holiday_date, task_assign=task_assign).delete()

    # Identify active employees on the holiday date
    active_employees = Employee.objects.filter(
        Q(doj__lte=instance.date),
        Q(relieving_date__isnull=True) | Q(relieving_date__gte=instance.date),
        status="active",
    )

    for emp in active_employees:
        # Avoid duplicates
        if not TimeSheet.objects.filter(
            employee=emp, date=instance.date, task_assign=task_assign
        ).exists():
            TimeSheet.objects.create(
                employee=emp,
                date=instance.date,
                task_assign=task_assign,
                task_hours=8,
                start_time=timezone.datetime.strptime("09:00", "%H:%M").time(),
                end_time=timezone.datetime.strptime("18:00", "%H:%M").time(),
                submitted=True,
                approved=True,
            )


LEAVE_PROJECT_MAP = {
    "casual_leave": "TKASS_01003",  # Casual Leave
    "sick_leave": "TKASS_01004",  # Sick Leave
    "earned_leave": "TKASS_01005",  # Earned Leave
    "comp_off": "TKASS_01006",  # Comp Off
    "lop": "TKASS_01008",  # Loss of Pay (if needed)
}


@receiver(post_save, sender=LeavesTaken)
def handle_timesheet_for_approved_leaves(sender, instance, created, **kwargs):
    leave_type = instance.leave_type.strip().lower()
    task_assign_id = LEAVE_PROJECT_MAP.get(leave_type)

    if instance.status != "approved" or not task_assign_id:
        return  # Only act on approval and mapped leave types

    try:
        task_assign = TaskAssign.objects.get(task_assign_id=task_assign_id)
    except TaskAssign.DoesNotExist:
        print(
            f"[WARN] TaskAssign {task_assign_id} not found for leave type {leave_type}"
        )
        return

    start_date = instance.start_date
    end_date = instance.end_date or start_date
    employee = instance.employee

    # Always clean up existing time entries for this leave period/type
    TimeSheet.objects.filter(
        employee=employee, task_assign=task_assign, date__range=[start_date, end_date]
    ).delete()

    current_date = start_date
    while current_date <= end_date:
        # Check if the date is a weekend or holiday using the Calendar table
        calendar_data = Calendar.objects.filter(date=current_date).first()

        if calendar_data and (calendar_data.is_weekend or calendar_data.is_holiday):
            # Skip weekend or holiday dates
            current_date += timedelta(days=1)
            continue

        duration = float(instance.duration or 1.0)
        hours = 4 if duration <= 0.5 else 8  # Half-day support

        if not TimeSheet.objects.filter(
            employee=employee, date=current_date, task_assign=task_assign
        ).exists():
            TimeSheet.objects.create(
                employee=employee,
                date=current_date,
                task_assign=task_assign,
                task_hours=hours,
                start_time=timezone.datetime.strptime("09:00", "%H:%M").time(),
                end_time=(
                    timezone.datetime.strptime("13:00", "%H:%M").time()
                    if hours == 4
                    else timezone.datetime.strptime("18:00", "%H:%M").time()
                ),
                submitted=True,
                approved=True,
            )
        current_date += timedelta(days=1)


@receiver(post_delete, sender=LeavesTaken)
def delete_related_timesheets_on_leave_deletion(sender, instance, **kwargs):
    leave_type = instance.leave_type.strip().lower()
    task_assign_id = LEAVE_PROJECT_MAP.get(leave_type)

    if not task_assign_id:
        return

    try:
        task_assign = TaskAssign.objects.get(task_assign_id=task_assign_id)
    except TaskAssign.DoesNotExist:
        return

    start_date = instance.start_date
    end_date = instance.end_date or start_date

    TimeSheet.objects.filter(
        employee=instance.employee,
        task_assign=task_assign,
        date__range=[start_date, end_date],
    ).delete()


@receiver(pre_save, sender=Employee)
def track_important_field_changes(sender, instance, **kwargs):
    try:
        old = Employee.objects.get(pk=instance.pk)
        instance._doj_changed = old.doj != instance.doj
        instance._probation_confirmation_changed = (
            old.probation_confirmation_date != instance.probation_confirmation_date
        )
        instance._contract_end_changed = (
            old.contract_end_date != instance.contract_end_date
        )
        instance._employment_type_changed = (
            old.employment_type != instance.employment_type
        )
    except Employee.DoesNotExist:
        instance._doj_changed = True
        instance._probation_confirmation_changed = True
        instance._contract_end_changed = True
        instance._employment_type_changed = True


@receiver(post_save, sender=Employee)
def handle_employee_leave_logic(sender, instance, created, **kwargs):
    if created:
        create_or_update_leaves_for_employee(instance)
    else:
        # Recalculate only if relevant fields changed
        if (
            getattr(instance, "_doj_changed", False)
            or getattr(instance, "_probation_confirmation_changed", False)
            or getattr(instance, "_contract_end_changed", False)
            or getattr(instance, "_employment_type_changed", False)
        ):
            create_or_update_leaves_for_employee(instance, is_update=True)


# @receiver(post_save, sender=Employee)
# def handle_employee_leave_logic(sender, instance, created, **kwargs):
#     if created:
#         create_or_update_leaves_for_employee(instance)

#     else:
#         try:
#             old_instance = Employee.objects.get(employee_id=instance.employee_id)
#         except Employee.DoesNotExist:
#             return

#         # Check for transition from Probation to Fulltime
#         if (
#             old_instance.employment_type == "Probation"
#             and instance.employment_type == "Fulltime"
#             and instance.probation_confirmation_date
#         ):
#             create_or_update_leaves_for_employee(instance, is_update=True)


@receiver(post_save, sender=Employee)
def create_or_update_hierarchy(sender, instance, created, **kwargs):
    """
    - Create Hierarchy if it doesn't exist
    - Sync designation, department
    - Auto-resolve reporting_to from employee.reporting_manager (by ID or code)
    """
    hierarchy, created_hierarchy = Hierarchy.objects.get_or_create(employee=instance)

    # Always update designation and department
    hierarchy.designation = instance.designation
    hierarchy.department = instance.department

    # Auto-resolve reporting_to
    if instance.reporting_manager:
        manager = (
            Employee.objects.filter(employee_id=instance.reporting_manager).first()
            or Employee.objects.filter(employee_code=instance.reporting_manager).first()
        )
        hierarchy.reporting_to = manager

    # Auto-resolve reporting_to
    if instance.second_reporting_manager:
        manager = (
            Employee.objects.filter(
                employee_id=instance.second_reporting_manager
            ).first()
            or Employee.objects.filter(
                employee_code=instance.second_reporting_manager
            ).first()
        )
        hierarchy.second_reporting_to = manager

    hierarchy.save()


# 1. Sync Employee.status → User.status
@receiver(post_save, sender=Employee)
def sync_employee_status_to_user(sender, instance, **kwargs):
    try:
        user = User.objects.get(employee_id=instance)
        if user.status != instance.status:
            user.status = instance.status
            user.save(update_fields=["status"])  # avoid triggering all signals again
    except User.DoesNotExist:
        pass


# 2. Sync User.status → Employee.status
@receiver(post_save, sender=User)
def sync_user_status_to_employee(sender, instance, **kwargs):
    employee = instance.employee_id
    employee = Employee.objects.filter(user=instance).first()
    if employee.status != instance.status:
        employee.status = instance.status
        employee.save(update_fields=["status"])


@receiver([post_save, post_delete], sender=Variation)
def update_variation_hours(sender, instance, **kwargs):
    project = instance.project
    if project:
        total_variation = (
            Variation.objects.filter(project=project).aggregate(Sum("hours"))[
                "hours__sum"
            ]
            or 0
        )
        project.variation_hours = total_variation
        project.save()


@receiver([post_save, post_delete], sender=TimeSheet)
def update_consumed_hours(sender, instance, **kwargs):
    task_assign = instance.task_assign
    if not task_assign:
        return

    building_assign = task_assign.building_assign
    if not building_assign:
        return

    project_assign = building_assign.project_assign
    if not project_assign or not project_assign.project:
        return

    project = project_assign.project
    total_consumed = (
        TimeSheet.objects.filter(
            task_assign__building_assign__project_assign__project=project, approved=True
        ).aggregate(Sum("task_hours"))["task_hours__sum"]
        or 0
    )

    project.consumed_hours = total_consumed
    project.save()


# @receiver(pre_save, sender=Calendar)
# def notify_on_calendar_flag_change(sender, instance, **kwargs):
#     if not instance.pk:
#         return  # It's a new record, not an update

#     try:
#         previous = Calendar.objects.get(pk=instance.pk)
#     except Calendar.DoesNotExist:
#         return
#     # Check if either is_holiday or is_weekend has changed
#     if (
#         previous.is_holiday != instance.is_holiday
#         or previous.is_weekend != instance.is_weekend
#     ):
#         date_str = instance.date.strftime("%d-%m-%Y")

#         if instance.is_holiday:
#             message = (
#                 f"Dear Team,\n\n"
#                 f"The day {date_str} is marked as a holiday on occasion of '{instance.notes or 'unspecified'}'.\n\n"
#                 "Regards,\nAdmin Team"
#             )
#         elif not instance.is_weekend and not instance.is_holiday:
#             message = f"The day {date_str} is marked as a working day."
#             message = (
#                 f"Dear Team,\n\n"
#                 f"The day {date_str} is marked as a working day because of '{instance.notes or 'unspecified'}'.\n\n"
#                 "Regards,\nAdmin Team"
#             )

#         subject = "Calendar Working day changed"

# send_mail(
#     subject,
#     message,
#     settings.DEFAULT_FROM_EMAIL,  # Replace with your configured from address
#     [settings.ALL_EMAIL],
#     # cc=[settings.ADMIN_EMAIL],  # Replace with your recipient(s)
#     fail_silently=False,
# )


# @receiver(post_save, sender=LeavesTaken)
# def create_leave_days_on_approval(sender, instance, created, **kwargs):
#     """
#     Automatically create LeaveDay records when a leave is approved or pending.
#     Ensures no overlapping leave days exist for the same employee.
#     """
#     if instance.status not in ["approved", "pending"]:
#         LeaveDay.objects.filter(leave_taken=instance).delete()
#         return

#     if not instance.start_date or not instance.end_date:
#         return

#     # Delete existing leave days linked to this specific leave (not others)
#     LeaveDay.objects.filter(leave_taken=instance).delete()

#     # Create or update leave days
#     current_date = instance.start_date
#     while current_date <= instance.end_date:
#         try:
#             LeaveDay.objects.update_or_create(
#                 employee=instance.employee,
#                 date=current_date,
#                 defaults={
#                     "leave_taken": instance,
#                     # "duration": 1.0,
#                     "duration": 0.5 if (instance.duration % 1) else 1.0,
#                     "leave_type": instance.leave_type,
#                     "status": instance.status,
#                 },
#             )
#         except IntegrityError:
#             # Handle conflict (another leave already covers this date)
#             print(
#                 f"Skipped overlapping leave day: {instance.employee} on {current_date}"
#             )
#         current_date += timedelta(days=1)


@receiver(post_save, sender=LeavesTaken)
def create_leave_days_on_approval(sender, instance, created, **kwargs):
    """
    Automatically create LeaveDay records when a leave is approved or pending.
    Skips weekends and holidays from Calendar.
    Ensures no overlapping leave days exist for the same employee.
    """
    # Only keep LeaveDay rows for pending/approved leaves
    if instance.status not in ["approved", "pending"]:
        LeaveDay.objects.filter(leave_taken=instance).delete()
        return

    if not instance.start_date or not instance.end_date:
        return

    # Remove old LeaveDay rows *for this leave only*
    LeaveDay.objects.filter(leave_taken=instance).delete()

    current_date = instance.start_date
    # Decide per-day duration (your existing logic)
    per_day_duration = 0.5 if (instance.duration and instance.duration % 1) else 1.0

    while current_date <= instance.end_date:
        # ---- calendar / weekend / holiday check ----
        cal = Calendar.objects.filter(date=current_date).first()

        is_weekend = False
        is_holiday = False

        if cal:
            is_weekend = cal.is_weekend
            is_holiday = cal.is_holiday
        else:
            # Fallback: treat Sat/Sun as weekend if calendar row missing
            # weekday(): Monday=0 ... Sunday=6
            is_weekend = current_date.weekday() >= 5

        if is_weekend or is_holiday:
            # Skip creating a LeaveDay for this date
            current_date += timedelta(days=1)
            continue

        # ---- create/update the working-day LeaveDay ----
        try:
            LeaveDay.objects.update_or_create(
                employee=instance.employee,
                date=current_date,
                defaults={
                    "leave_taken": instance,
                    "duration": per_day_duration,
                    "leave_type": instance.leave_type,
                    "status": instance.status,
                },
            )
        except IntegrityError:
            # Another approved leave already occupies this date for this employee
            print(
                f"Skipped overlapping leave day: {instance.employee} on {current_date}"
            )

        current_date += timedelta(days=1)


@receiver(post_delete, sender=LeavesTaken)
def delete_leave_days_on_leave_delete(sender, instance, **kwargs):
    """
    When a LeavesTaken record is deleted:
      - Remove ALL related LeaveDay rows.
      - Recalculate the MonthlyLeaveBalance for the affected months.
    """

    #  Delete the LeaveDay rows linked to this leave
    LeaveDay.objects.filter(leave_taken=instance).delete()

    # If no valid dates, skip recalculation
    if not instance.start_date or not instance.end_date:
        return

    emp = instance.employee
    if not emp:
        return



# below for the leave balance calculation


def _rebuild_month(employee_id, year, month):
    """Re-aggregate the month for a single employee from LeaveDay (approved)."""
    qs = (
        LeaveDay.objects.approved()
        .filter(employee_id=employee_id, date__year=year, date__month=month)
        .values("leave_type")
        .annotate(total=Sum("duration"))
    )

    # Start with zeros
    totals = {
        "casual_leave_availed": Decimal("0.0"),
        "sick_leave_availed": Decimal("0.0"),
        "comp_off_availed": Decimal("0.0"),
        "earned_leave_availed": Decimal("0.0"),
    }

    # Map your leave_type strings to the model fields above
    FIELD_MAP = {
        "casual": "casual_leave_availed",
        "sick": "sick_leave_availed",
        "comp_off": "comp_off_availed",
        "earned": "earned_leave_availed",
    }

    for row in qs:
        fld = FIELD_MAP.get(row["leave_type"])
        if fld:
            totals[fld] = row["total"] or Decimal("0.0")

    obj, _ = MonthlyLeaveAvailed.objects.get_or_create(
        employee_id=employee_id, year=year, month=month, defaults=totals
    )
    for k, v in totals.items():
        setattr(obj, k, v)
    obj.save(update_fields=list(totals.keys()))


def _touch_month(instance: LeaveDay):
    y, m = instance.date.year, instance.date.month
    _rebuild_month(instance.employee_id, y, m)


@receiver(post_save, sender=LeaveDay)
def leave_day_saved(sender, instance: LeaveDay, **kwargs):
    _touch_month(instance)


@receiver(post_delete, sender=LeaveDay)
def leave_day_deleted(sender, instance: LeaveDay, **kwargs):
    _touch_month(instance)


# ---- normalization exactly to your DB keys ----
# Your LeaveDay.leave_type should already be one of these;
# if not, adapt normalize() to map variants.
VALID_TYPES = {"casual_leave", "sick_leave", "comp_off", "earned_leave"}


def normalize(leave_type: str) -> str:
    return leave_type.strip().lower() if leave_type else ""


def _zero_dict():
    return {
        "casual_leave": Decimal("0.0"),
        "sick_leave": Decimal("0.0"),
        "comp_off": Decimal("0.0"),
        "earned_leave": Decimal("0.0"),
    }


def _month_availed(employee_id: int, year: int, month: int):
    """
    Sum approved LeaveDay.duration per leave_type for the (year, month).
    Only keys in VALID_TYPES are counted; others ignored.
    """
    rows = (
        LeaveDay.objects.filter(
            employee_id=employee_id,
            status="approved",
            date__year=year,
            date__month=month,
        )
        .values("leave_type")
        .annotate(total=Coalesce(Sum("duration"), Decimal("0.0")))
    )

    av = _zero_dict()
    for r in rows:
        lt = normalize(r["leave_type"])
        if lt in VALID_TYPES:
            av[lt] = r["total"] or Decimal("0.0")
    return av


def _comp_off_earned(employee_id: str, year: int, month: int) -> Decimal:
    """
    Sum of Comp-Off credits earned in the month = APPROVED compoff requests
    whose 'date' falls in (year, month).
    """
    return (
        CompOffRequest.objects.filter(
            employee_id=employee_id,
            status="approved",
            date__year=year,
            date__month=month,
        )
        .aggregate(s=Coalesce(Sum("duration"), Decimal("0.0")))
        .get("s", Decimal("0.0"))
    )


def _get_january_opening(employee_id: int, year: int):
    """
    Opening for January comes from LeaveOpeningBalance (or zeros if missing).
    """
    opening = _zero_dict()
    ob = LeaveOpeningBalance.objects.filter(employee_id=employee_id, year=year).first()
    if ob:
        opening["casual_leave"] = ob.casual_leave_opening or Decimal("0.0")
        opening["sick_leave"] = ob.sick_leave_opening or Decimal("0.0")
        opening["comp_off"] = ob.comp_off_opening or Decimal("0.0")
        opening["earned_leave"] = ob.earned_leave_opening or Decimal("0.0")
    return opening


@transaction.atomic
def rebuild_monthly_balances(employee_id: int, year: int, start_month: int):
    """
    Recompute MonthlyLeaveBalance for employee/year from start_month..12.

    Logic per month m:
      opening(m)  = january_opening if m == 1 else previous_month.balance
      availed(m)  = sum(approved LeaveDay by type for (year, m))
      balance(m)  = opening(m) - availed(m)          # for each type
      save/update MonthlyLeaveBalance(m)

    Notes:
      * If you accrue comp-off "earned" separately, add + earned(m) into comp_off.
      * If editing January, this cascades through the whole year — desired.
    """
    # Ensure start_month bounds
    m0 = max(1, min(12, start_month))

    # Seed opening for the first month we will compute
    if m0 == 1:
        opening = _get_january_opening(employee_id, year)
    else:
        prev = MonthlyLeaveBalance.objects.filter(
            employee_id=employee_id, year=year, month=m0 - 1
        ).first()
        if prev:
            opening = {
                "casual_leave": prev.casual_leave_balance,
                "sick_leave": prev.sick_leave_balance,
                "comp_off": prev.comp_off_balance,
                "earned_leave": prev.earned_leave_balance,
            }
        else:
            # If the previous month record is missing, bootstrap from January opening
            # and rebuild from January to keep chain consistent.
            opening = _get_january_opening(employee_id, year)
            m0 = 1  # rebuild whole year forward

    # Walk months m0..12
    for m in range(m0, 12 + 1):
        av = _month_availed(employee_id, year, m)
        co_earned = _comp_off_earned(employee_id, year, m)

        # If you have comp-off earned accruals per month, add here, e.g.:
        # earned_comp = _comp_off_earned(employee_id, year, m)   # implement if needed
        # closing["comp_off"] = opening["comp_off"] + earned_comp - av["comp_off"]
        closing = {
            "casual_leave": opening["casual_leave"] - av["casual_leave"],
            "sick_leave": opening["sick_leave"] - av["sick_leave"],
            # NOTE: comp_off adds earned credits for the month
            "comp_off": opening["comp_off"] + co_earned - av["comp_off"],
            "earned_leave": opening["earned_leave"] - av["earned_leave"],
        }

        obj, _ = MonthlyLeaveBalance.objects.get_or_create(
            employee_id=employee_id,
            year=year,
            month=m,
            defaults=dict(
                casual_leave_balance=closing["casual_leave"],
                sick_leave_balance=closing["sick_leave"],
                comp_off_balance=closing["comp_off"],
                earned_leave_balance=closing["earned_leave"],
            ),
        )
        # Update even if it existed
        obj.casual_leave_balance = closing["casual_leave"]
        obj.sick_leave_balance = closing["sick_leave"]
        obj.comp_off_balance = closing["comp_off"]
        obj.earned_leave_balance = closing["earned_leave"]
        obj.save(
            update_fields=[
                "casual_leave_balance",
                "sick_leave_balance",
                "comp_off_balance",
                "earned_leave_balance",
            ]
        )

        # Next month opening = this month closing
        opening = closing


@receiver(post_save, sender=LeaveDay)
def leave_day_saved(sender, instance: LeaveDay, created, **kwargs):
    # Rebuild from the affected month forward in the same year
    rebuild_monthly_balances(
        employee_id=instance.employee_id,
        year=instance.date.year,
        start_month=instance.date.month,
    )


@receiver(post_delete, sender=LeaveDay)
def leave_day_deleted(sender, instance: LeaveDay, **kwargs):
    rebuild_monthly_balances(
        employee_id=instance.employee_id,
        year=instance.date.year,
        start_month=instance.date.month,
    )


@receiver(post_save, sender=LeaveOpeningBalance)
def leave_opening_saved(sender, instance: LeaveOpeningBalance, created, **kwargs):
    """
    Whenever the opening row is created/edited, rebuild the whole year Jan..Dec
    so monthly openings/closings reflect the new January opening.
    """
    with transaction.atomic():
        rebuild_monthly_balances(
            employee_id=instance.employee_id,
            year=instance.year,
            start_month=1,  # IMPORTANT: start from January
        )


@receiver(post_delete, sender=LeaveOpeningBalance)
def leave_opening_deleted(sender, instance: LeaveOpeningBalance, **kwargs):
    """
    If an opening row is deleted, treat January opening as 0.0 and rebuild Jan..Dec.
    (Adjust if you prefer to also delete the MonthlyLeaveBalance rows.)
    """
    with transaction.atomic():
        rebuild_monthly_balances(
            employee_id=instance.employee_id,
            year=instance.year,
            start_month=1,
        )


@receiver(post_save, sender=CompOffRequest)
def compoff_saved(sender, instance: CompOffRequest, **kwargs):
    """
    Recompute from the month of the comp-off 'date' forward whenever the record
    is saved. This covers:
      - status flip to 'approved'
      - duration/date edits
      - manager re-approval, etc.
    """
    y, m = instance.date.year, instance.date.month
    rebuild_monthly_balances(employee_id=instance.employee_id, year=y, start_month=m)


@receiver(post_delete, sender=CompOffRequest)
def compoff_deleted(sender, instance: CompOffRequest, **kwargs):
    y, m = instance.date.year, instance.date.month
    rebuild_monthly_balances(employee_id=instance.employee_id, year=y, start_month=m)
