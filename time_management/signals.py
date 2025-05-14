from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Employee, LeavesAvailable, Hierarchy
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
