from django.core.management.base import BaseCommand
from django.utils import timezone
from time_management.models import (
    LeavesAvailable,
)  # Adjust this import path to your app
from datetime import datetime


class Command(BaseCommand):
    help = "Reset leaves for all employees annually on Jan 1st"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()

        if today.month == 1 and today.day == 1:
            leaves = LeavesAvailable.objects.all()
            for leave in leaves:
                emp = leave.employee
                print("employee type", emp.employment_type)
                if emp and emp.employment_type == "Fulltime":
                    leave.sick_leave = 6
                    leave.casual_leave = 6
                    leave.comp_off = 0
                    leave.earned_leave += 6  # carry forward + new
                    leave.save()
            self.stdout.write(
                self.style.SUCCESS(" Annual leave reset completed successfully.")
            )
        else:
            self.stdout.write(" This script should only run on January 1st.")
