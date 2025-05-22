from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum

from django.utils import timezone
from .models import Employee, LeavesAvailable, Hierarchy, User, Variation, TimeSheet
from time_management.management.commands.utils import (
    calculate_leave_entitlement,
    create_or_update_leaves_for_employee
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
            task_assign__building_assign__project_assign__project=project
        ).aggregate(Sum("task_hours"))["task_hours__sum"]
        or 0
    )

    project.consumed_hours = total_consumed
    project.save()
