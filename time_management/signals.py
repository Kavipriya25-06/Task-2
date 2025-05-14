from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Employee, LeavesAvailable, Hierarchy, User
from time_management.management.commands.utils import (
    calculate_leave_entitlement,
)  # create this in utils.py


@receiver(post_save, sender=Employee)
def create_leave_record(sender, instance, created, **kwargs):
    """
    - Create leave record if it doesn't exist

    """

    if created and not LeavesAvailable.objects.filter(employee=instance).exists():
        if instance.doj:
            leave_count = calculate_leave_entitlement(instance.doj)
        else:
            leave_count = 0

        LeavesAvailable.objects.create(
            employee=instance,
            sick_leave=leave_count,
            casual_leave=leave_count,
            comp_off=0,
            earned_leave=leave_count,
        )


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
