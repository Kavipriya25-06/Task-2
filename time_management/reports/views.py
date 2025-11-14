from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Sum, Q, Count
from calendar import monthrange
from collections import defaultdict

import csv
import io
from datetime import datetime
from django.http import HttpResponse
from django.db import connection
from datetime import datetime, timedelta, date, time


from ..models import (
    Project,
    ProjectAssign,
    Building,
    BuildingAssign,
    Task,
    TaskAssign,
    Variation,
    LeavesTaken,
    TimeSheet,
    LeavesAvailable,
    Employee,
    Calendar,
    BiometricData,
)

from time_management.reports.serializers import (
    ProjectHoursSerializer,
    ProjectWeeklyHoursSerializer,
    ProjectMonthlyHoursSerializer,
    ProjectYearlyHoursSerializer,
    TimeSheetTaskSerializer,
    LeavesAvailableSerializer,
    EmployeeLOPSerializer,
    ProjectDepartmentWeeklyHoursSerializer,
    ProjectDepartmentWeeklyStatsSerializer,
    LeavesFullAvailableSerializer,
    EmployeeMonthlyAttendanceSerializer,
)
from time_management.project.serializers import ProjectSerializer
from time_management.building.serializers import BuildingAndAssignSerializer
from time_management.leaves_taken.serializers import (
    LeavesTakenSerializer,
    LeaveRequestSerializer,
)
from time_management.task.serializers import TaskSerializer


@api_view(["GET"])
def hours_project_view(request, project_id=None):
    if project_id:
        try:
            project = Project.objects.get(project_id=project_id)
            serializer = ProjectHoursSerializer(project)
        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

    else:
        project = Project.objects.all()
        serializer = ProjectHoursSerializer(project, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def weekly_hours_project(request, project_id=None):
    if project_id:
        try:
            project = Project.objects.get(project_id=project_id)
            serializer = ProjectWeeklyHoursSerializer(project)
        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

    else:
        project = Project.objects.all()
        serializer = ProjectWeeklyHoursSerializer(project, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def weekly_employees(request, department=None):

    year = request.query_params.get("year")

    if not year:
        year = date.today().year
        print("year is ", year)

    year = int(year)

    serializer = ProjectDepartmentWeeklyStatsSerializer(
        Calendar(),  # Dummy instance (since we're using only class-level logic)
        context={"year": year, "department": department},
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def department_weekly_hours_project(request, department=None, project_id=None):

    year = request.query_params.get("year")

    if not year:
        year = date.today().year
        print("year is ", year)

    if department:
        try:
            project = Project.objects.all()
            serializer = ProjectDepartmentWeeklyHoursSerializer(
                project,
                many=True,
                context={"request": request, "department": department, "year": year},
            )
        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

    else:
        project = Project.objects.all()
        serializer = ProjectDepartmentWeeklyHoursSerializer(
            project,
            many=True,
            context={"request": request, "department": department, "year": year},
        )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def monthly_hours_project(request, project_id=None):
    if project_id:
        try:
            project = Project.objects.get(project_id=project_id)
            serializer = ProjectMonthlyHoursSerializer(project)
        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

    else:
        project = Project.objects.all()
        serializer = ProjectMonthlyHoursSerializer(project, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def yearly_hours_project(request, project_id=None):
    if project_id:
        try:
            project = Project.objects.get(project_id=project_id)
            serializer = ProjectYearlyHoursSerializer(project)
        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

    else:
        project = Project.objects.all()
        serializer = ProjectYearlyHoursSerializer(project, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_last_project(request):
    if request.method == "GET":
        try:
            last_instance = Project.objects.order_by("project_id").last()
            serializer = ProjectSerializer(last_instance)
            return Response(serializer.data)
        except Project.DoesNotExist:
            return Response(
                {"error": "project record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["GET"])
def get_last_building(request, project_id=None):
    if request.method == "GET":
        if project_id:
            try:
                projectBuildings = BuildingAssign.objects.filter(
                    project_assign__project=project_id
                )
                last_building = projectBuildings.order_by("building_assign_id").last()
                print("last building", last_building)
                # last_instance = Project.objects.order_by("project_id").last()
                serializer = BuildingAndAssignSerializer(last_building)
                # serializer = ProjectSerializer(last_instance)
                return Response(serializer.data)
            except BuildingAssign.DoesNotExist:
                return Response(
                    {"error": "project record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"error": "project record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["GET"])
def get_last_task(request):
    if request.method == "GET":
        try:
            last_instance = Task.objects.order_by("task_id").last()
            serializer = TaskSerializer(last_instance)
            return Response(serializer.data)
        except Project.DoesNotExist:
            return Response(
                {"error": "Task record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["GET"])
def year_leaves(request):
    year = request.query_params.get("year")
    try:
        if year:
            yearly_leaves = LeavesTaken.objects.filter(
                start_date__year=year, status="approved"
            ).order_by("start_date")
        else:
            yearly_leaves = LeavesTaken.objects.all()
        serializer = LeaveRequestSerializer(yearly_leaves, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except LeavesTaken.DoesNotExist:
        return Response(
            {"error": "Employee Leave record not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
def employee_report_week(request, employee_id=None):

    todaystr = request.query_params.get("today")  # <-- Get the date from filter params
    if todaystr:
        today = datetime.strptime(todaystr, "%Y-%m-%d").date()
    else:
        today = False

    if employee_id:
        try:
            employee_timesheet = TimeSheet.objects.filter(
                employee=employee_id, approved=True
            )
        except TimeSheet.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        # employees = emp_under_manager(manager)

        # timesheet_qs = TimeSheet.objects.filter(employee__in=employees)
        if today:
            weekday = today.weekday()
            start = today - timedelta(days=weekday)
            end = start + timedelta(days=6)
            timesheet_entries = employee_timesheet.filter(
                date__range=(start, end)
            ).order_by("date")

            serializer = TimeSheetTaskSerializer(timesheet_entries, many=True)
        else:
            serializer = TimeSheetTaskSerializer(employee_timesheet, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        objs = TimeSheet.objects.all()
        if today:
            weekday = today.weekday()
            start = today - timedelta(days=weekday)
            end = start + timedelta(days=6)
            timesheet_entries = objs.filter(date__range=(start, end)).order_by("date")

            serializer = TimeSheetTaskSerializer(timesheet_entries, many=True)
        else:
            serializer = TimeSheetTaskSerializer(objs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def leaves_available_report(request):
    year = request.query_params.get("year")
    if request.method == "GET":
        try:
            obj = LeavesAvailable.objects.all()
            serializer = LeavesFullAvailableSerializer(
                obj, many=True, context={"request": request, "year": year}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except LeavesAvailable.DoesNotExist:
            return Response(
                {"error": "Leave record with leave id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["GET"])
def active_leaves_available_report(request):
    year = request.query_params.get("year")
    if request.method == "GET":
        try:
            obj = LeavesAvailable.objects.filter(employee__user__status="active")
            serializer = LeavesFullAvailableSerializer(
                obj, many=True, context={"request": request, "year": year}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except LeavesAvailable.DoesNotExist:
            return Response(
                {"error": "Leave record with leave id not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["GET"])
# @parser_classes([MultiPartParser, FormParser])
def employee_lop_view(request):
    # GET (single or list)
    year = request.query_params.get("year")
    if request.method == "GET":
        try:
            employees = Employee.objects.all()
            serializer = EmployeeLOPSerializer(
                employees, many=True, context={"request": request, "year": year}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
            )


def month_bounds_count(y, m):
    start = date(y, m, 1)
    end = date(y, m, monthrange(y, m)[1])
    return start, end


def month_label(y, m):
    return date(y, m, 1).strftime("%b %Y")  # e.g. "Feb 2025"


def closing_headcount(day):
    # employees active on this day
    return Employee.objects.filter(doj__lte=day).filter(
        Q(relieving_date__isnull=True, resignation_date__isnull=True)
        | Q(relieving_date__gte=day)
        | Q(resignation_date__gte=day)
    )


def resigned_in_month(start, end):
    # end-date in the month (prefer relieving_date; else resignation_date)
    return Employee.objects.filter(
        Q(relieving_date__range=(start, end))
        | (Q(relieving_date__isnull=True) & Q(resignation_date__range=(start, end)))
    )


def new_joiners_in_month(start, end):
    return Employee.objects.filter(doj__range=(start, end))


@api_view(["GET"])
def attrition_report(request):
    """
    GET /hr/attrition-report/?year=2025

    Returns months only up to LAST month for the given year.
    - Current year: months 1..(today.month-1)
    - Past year: months 1..12
    - Future year: []
    """
    today = date.today()
    try:
        year = int(request.query_params.get("year", today.year))
    except (TypeError, ValueError):
        year = today.year

    # Determine last month to include
    if year > today.year:
        return Response([], status=status.HTTP_200_OK)
    if year < today.year:
        max_month = 12
    else:
        max_month = today.month - 1  # up to last month (exclude current month)

    if max_month < 1:
        # e.g., January current year → no months to show
        return Response([], status=status.HTTP_200_OK)

    trend = []

    for m in range(1, max_month + 1):
        start, end = month_bounds_count(year, m)
        opening_day = start - timedelta(days=1)

        opening_count = closing_headcount(opening_day).count()
        closing_qs = closing_headcount(end)

        # snapshot by employment type at month-end
        type_counts = dict(
            closing_qs.values("employment_type")
            .annotate(c=Count("employee_id"))
            .values_list("employment_type", "c")
        )
        fulltime = type_counts.get("Fulltime", 0)
        interns = type_counts.get("Internship", 0)
        trainees = type_counts.get("Trainee", 0)
        contract = type_counts.get("Contract", 0)

        total_resources = fulltime + interns + trainees + contract

        resigned = resigned_in_month(start, end).count()
        new_recruits = new_joiners_in_month(start, end).count()

        avg_hc = (
            (opening_count + total_resources) / 2
            if (opening_count + total_resources) > 0
            else 0
        )
        attrition_rate = round((resigned / avg_hc) * 100, 1) if avg_hc else 0.0

        trend.append(
            {
                "month": month_label(year, m),
                "fulltime": fulltime,
                "interns": interns,
                "trainees": trainees,
                "contract": contract,
                "total_resources": total_resources,
                "resigned": resigned,
                "new_recruits": new_recruits,
                "attrition_rate": attrition_rate,
            }
        )

    return Response(trend, status=status.HTTP_200_OK)


# attendance report below


def month_bounds(y: int, m: int):
    days = monthrange(y, m)[1]
    return date(y, m, 1), date(y, m, days)


def daterange(d1: date, d2: date):
    """Inclusive date range generator."""
    cur = d1
    while cur <= d2:
        yield cur
        cur = cur + timedelta(days=1)


@api_view(["GET"])
def monthly_attendance_summary(request):
    """
    GET /hr/monthly-attendance-summary/?year=2025&month=10

    Returns a list of employees (active during the month) with:
      department, name, absent, notes, late, od, wfh

    Rules:
    - Absent: count *working days* covered by APPROVED LeavesTaken that
              overlap the month (Calendar.is_weekend/is_holiday excluded)
    - Notes:  concatenation of all reasons from those approved LeavesTaken
    - Late:   BiometricData.in_time > 09:15 on working days
    - OD/WFH: BiometricData.status == 'OD' / 'WFH' on working days
    """
    # --- 1) Parse inputs & month window ---
    today = date.today()
    try:
        year = int(request.query_params.get("year", today.year))
        month = int(request.query_params.get("month", today.month))
    except (TypeError, ValueError):
        return Response(
            {"error": "Invalid year/month."}, status=status.HTTP_400_BAD_REQUEST
        )

    start_date, end_date = month_bounds(year, month)

    # --- 2) Working days set from Calendar ---
    working_days = set(
        Calendar.objects.filter(
            date__range=(start_date, end_date),
            is_weekend=False,
            is_holiday=False,
        ).values_list("date", flat=True)
    )

    # --- 3) Employees active in this month ---
    employees = (
        Employee.objects.filter(doj__lte=end_date)
        .filter(Q(relieving_date__isnull=True) | Q(relieving_date__gte=start_date))
        # optional: limit to active/resigned only
        .filter(status__in=["active", "resigned", "inactive"])
        .only("pk", "employee_name", "department")
    )

    emp_ids = list(employees.values_list("pk", flat=True))

    # --- 4) Pre-aggregate LeavesTaken (approved & overlapping the month) ---
    leaves = (
        LeavesTaken.objects.filter(
            employee_id__in=emp_ids,
            status="approved",
        )
        .filter(Q(start_date__lte=end_date) & Q(end_date__gte=start_date))
        .only("employee_id", "start_date", "end_date", "reason")
    )

    # For each employee, count number of working-days overlapped by the leave.
    absent_by_emp = defaultdict(int)
    notes_by_emp = defaultdict(list)

    for lv in leaves:
        # overlap window
        s = max(lv.start_date, start_date)
        e = min(lv.end_date, end_date)
        if s > e:
            continue
        # count only working days within overlap
        # (if you support half days, adjust here)
        for d in daterange(s, e):
            if d in working_days:
                absent_by_emp[lv.employee_id] += 1
        if lv.reason:
            notes_by_emp[lv.employee_id].append(lv.reason.strip())

    # --- 5) Pre-aggregate BiometricData for the month (working days only) ---
    bio_qs = BiometricData.objects.filter(
        employee_id__in=emp_ids,
        date__range=(start_date, end_date),
    ).only("employee_id", "date", "status", "in_time")

    late_cutoff = time(9, 15)  # 09:15:00

    late_by_emp = defaultdict(int)
    od_by_emp = defaultdict(int)
    wfh_by_emp = defaultdict(int)

    # Only count events on working days
    for b in bio_qs:
        if b.date not in working_days:
            continue
        # Late: strictly greater than 09:15
        if b.in_time and b.in_time > late_cutoff:
            late_by_emp[b.employee_id] += 1

        st = (b.status or "").strip().lower()
        if st == "od":
            od_by_emp[b.employee_id] += 1
        elif st == "wfh":
            wfh_by_emp[b.employee_id] += 1

    # --- 6) Build summaries dict for serializer context ---
    summaries = {}
    for emp_id in emp_ids:
        summaries[emp_id] = {
            "absent": absent_by_emp.get(emp_id, 0),
            "notes": "; ".join(notes_by_emp.get(emp_id, [])),
            "late": late_by_emp.get(emp_id, 0),
            "od": od_by_emp.get(emp_id, 0),
            "wfh": wfh_by_emp.get(emp_id, 0),
        }

    # If you wish to hide rows with all zeros, uncomment:
    # employees = [e for e in employees if any(summaries[e.pk].values())]

    # Sort by absent desc (like your sample)
    employees = sorted(
        employees, key=lambda e: summaries.get(e.pk, {}).get("absent", 0), reverse=True
    )

    serializer = EmployeeMonthlyAttendanceSerializer(
        employees, many=True, context={"summaries": summaries}
    )
    return Response(serializer.data, status=status.HTTP_200_OK)
