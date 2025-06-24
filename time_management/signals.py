from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, Q

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


@receiver(post_save, sender=Employee)
def handle_employee_leave_logic(sender, instance, created, **kwargs):
    if created:
        create_or_update_leaves_for_employee(instance)

    else:
        try:
            old_instance = Employee.objects.get(employee_id=instance.employee_id)
        except Employee.DoesNotExist:
            return

        # Check for transition from Probation to Fulltime
        if (
            old_instance.employment_type == "Probation"
            and instance.employment_type == "Fulltime"
            and instance.probation_confirmation_date
        ):
            create_or_update_leaves_for_employee(instance, is_update=True)


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
