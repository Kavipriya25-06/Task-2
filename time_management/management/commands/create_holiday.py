from datetime import date
from django.utils import timezone
from django.db.models import Q
from time_management.models import Calendar, Employee, TaskAssign, TimeSheet


def create_timesheets_for_today_if_holiday():
    today = date.today()
    calendar = Calendar.objects.filter(date=today, is_holiday=True).first()
    if not calendar:
        return

    try:
        task_assign = TaskAssign.objects.get(task_assign_id="TKASS_01011")
    except TaskAssign.DoesNotExist:
        print("[WARN] Holiday TaskAssign missing.")
        return

    active_employees = Employee.objects.filter(
        status="active",
        doj__lte=today,
    ).filter(Q(relieving_date__isnull=True) | Q(relieving_date__gte=today))

    for emp in active_employees:
        if not TimeSheet.objects.filter(
            employee=emp, date=today, task_assign=task_assign
        ).exists():
            TimeSheet.objects.create(
                employee=emp,
                date=today,
                task_assign=task_assign,
                task_hours=8,
                start_time=timezone.datetime.strptime("09:00", "%H:%M").time(),
                end_time=timezone.datetime.strptime("18:00", "%H:%M").time(),
                submitted=True,
                approved=True,
            )
