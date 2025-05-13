from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Employee, LeavesAvailable
from time_management.management.commands.utils import calculate_leave_entitlement  # create this in utils.py


@receiver(post_save, sender=Employee)
def create_leave_record(sender, instance, created, **kwargs):
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
