from django.core.management.base import BaseCommand
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from time_management.models import Employee  # Update the import based on your app name


class Command(BaseCommand):
    help = "Update arris_experience and total_experience for all employees"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        employees = Employee.objects.all()

        for emp in employees:
            if emp.doj:
                delta = relativedelta(today, emp.doj)
                arris_months = delta.years * 12 + delta.months
                emp.aero360_experience = arris_months
                emp.total_experience = arris_months + (emp.previous_experience or 0)
                emp.experience_in_years = round(emp.total_experience / 12, 2)
                emp.save()

            if emp.dob:
                delta = relativedelta(today, emp.dob)
                age_months = delta.years * 12 + delta.months
                emp.age = age_months // 12
                emp.save()

        self.stdout.write(
            self.style.SUCCESS("Successfully updated experience for all employees")
        )
