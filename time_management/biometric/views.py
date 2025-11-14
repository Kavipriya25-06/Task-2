from rest_framework.viewsets import ModelViewSet
import uuid
from django.db.models import OuterRef, Subquery
from ..models import BiometricData, Employee, Calendar, LeaveDay
from time_management.biometric.serializers import (
    BiometricDataSerializer,
    BiometricTaskDataSerializer,
    EmployeeAttendanceSerializer,
    EmployeeWeekSerializer,
)
from time_management.hierarchy.serializers import (
    emp_under_manager,
    get_emp_under_manager,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from datetime import datetime, timedelta, date as date_cls
from django.http import JsonResponse
from django.db.models import Prefetch, Q


def generate_group_id(employee_code):
    # Using a combination of a timestamp and random UUID for uniqueness
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # random_suffix = uuid.uuid4().hex[:8]  # 8-character random suffix
    random_suffix = employee_code  # employee code
    return f"BULK_{timestamp}_{random_suffix}"


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def biometric_data_api(request, biometric_id=None, employee_id=None):
    if request.method == "GET":
        todaystr = request.query_params.get(
            "today"
        )  # <-- Get the date from filter params
        if todaystr:
            today = datetime.strptime(todaystr, "%Y-%m-%d").date()
        else:
            today = False

        if biometric_id:
            try:
                obj = BiometricData.objects.get(biometric_id=biometric_id)
                serializer = BiometricTaskDataSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except BiometricData.DoesNotExist:
                return Response(
                    {"error": "Biometric record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        elif employee_id:
            try:
                obj = BiometricData.objects.filter(employee_id=employee_id)
                if today:
                    month = today.month
                    print("This month", today.strftime("%m"), month)
                    calendar_entries = obj.filter(date__month=month).order_by("date")
                else:
                    calendar_entries = obj

                serializer = BiometricTaskDataSerializer(calendar_entries, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except BiometricData.DoesNotExist:
                return Response(
                    {"error": "Biometric record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = BiometricData.objects.all()
            serializer = BiometricTaskDataSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = BiometricDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Biometric record added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not biometric_id:
            return Response(
                {"error": "Biometric ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = BiometricData.objects.get(biometric_id=biometric_id)
        except BiometricData.DoesNotExist:
            return Response(
                {"error": "Biometric record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = BiometricDataSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Biometric record updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not biometric_id:
            return Response(
                {"error": "Biometric ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = BiometricData.objects.get(biometric_id=biometric_id)
            obj.delete()
            return Response(
                {"message": "Biometric record deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except BiometricData.DoesNotExist:
            return Response(
                {"error": "Biometric record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def biometric_view_api(request, biometric_id=None, employee_id=None):
    if request.method == "GET":
        todaystr = request.query_params.get(
            "today"
        )  # <-- Get the date from filter params
        if todaystr:
            today = datetime.strptime(todaystr, "%Y-%m-%d").date()
        else:
            today = False

        if biometric_id:
            try:
                obj = BiometricData.objects.get(biometric_id=biometric_id)
                serializer = BiometricDataSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except BiometricData.DoesNotExist:
                return Response(
                    {"error": "Biometric record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        elif employee_id:
            try:
                obj = BiometricData.objects.filter(employee_id=employee_id)
                if today:
                    month = today.month
                    print("This month", today.strftime("%m"), month)
                    calendar_entries = obj.filter(date__month=month).order_by("date")
                else:
                    calendar_entries = obj

                serializer = BiometricDataSerializer(calendar_entries, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except BiometricData.DoesNotExist:
                return Response(
                    {"error": "Biometric record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = BiometricData.objects.all()
            serializer = BiometricDataSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = BiometricDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Biometric record added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not biometric_id:
            return Response(
                {"error": "Biometric ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = BiometricData.objects.get(biometric_id=biometric_id)
        except BiometricData.DoesNotExist:
            return Response(
                {"error": "Biometric record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = BiometricDataSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Biometric record updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not biometric_id:
            return Response(
                {"error": "Biometric ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = BiometricData.objects.get(biometric_id=biometric_id)
            obj.delete()
            return Response(
                {"message": "Biometric record deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except BiometricData.DoesNotExist:
            return Response(
                {"error": "Biometric record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["GET"])
def attendance(request, employee_id=None):
    if employee_id:
        try:
            manager = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        employees = get_emp_under_manager(manager)

        biometric_qs = BiometricData.objects.filter(employee__in=employees)

        serializer = BiometricDataSerializer(biometric_qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        objs = BiometricData.objects.all()
        serializer = BiometricDataSerializer(objs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def _week_bounds(day: date_cls):
    weekday = day.weekday()  # Monday=0..Sunday=6
    start = day - timedelta(days=weekday)
    end = start + timedelta(days=6)
    return start, end


@api_view(["GET"])
def attendance_track(request, employee_id=None):
    # Parse ?today=YYYY-MM-DD (optional)
    today_param = request.query_params.get("today")
    if today_param:
        try:
            today = datetime.strptime(today_param, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid 'today' format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    else:
        today = datetime.now().date()

    start, end = _week_bounds(today)

    # Resolve which employees to include
    if employee_id:
        try:
            manager = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        team = get_emp_under_manager(manager)
        # Normalize to a queryset of employees incl. manager
        if hasattr(team, "values"):
            employees_qs = (team | Employee.objects.filter(pk=manager.pk)).distinct()
        else:
            ids = [e.pk for e in team] + [manager.pk]
            employees_qs = Employee.objects.filter(pk__in=ids)
    else:
        employees_qs = Employee.objects.all()

    employees = list(
        employees_qs.only("employee_id", "employee_name", "department", "designation")
    )
    if not employees:
        return Response([], status=status.HTTP_200_OK)

    emp_ids = [e.pk for e in employees]

    # Fetch the 7 calendar days once
    calendar_days = list(
        Calendar.objects.filter(date__range=(start, end)).order_by("date")
    )
    # Safety: ensure we always have 7 rows (if your Calendar table is guaranteed full, this is not needed)
    if len(calendar_days) != 7:
        # Optional: backfill missing dates from plain date range
        # but best is to ensure Calendar is populated for all dates
        pass

    # Fetch biometric & leave rows for those employees in the week range
    biometric_rows = BiometricData.objects.select_related("employee").filter(
        employee_id__in=emp_ids, date__range=(start, end)
    )
    leave_rows = LeaveDay.objects.select_related("employee").filter(
        employee_id__in=emp_ids, date__range=(start, end)
    )

    # Build fast lookup maps keyed by (employee_pk, date)
    bio_map = {(row.employee_id, row.date): row for row in biometric_rows}
    leave_map = {(row.employee_id, row.date): row for row in leave_rows}

    # Serialize employees with week detail
    ser = EmployeeWeekSerializer(
        employees,
        many=True,
        context={
            "calendar_days": calendar_days,
            "bio_map": bio_map,
            "leave_map": leave_map,
        },
    )
    return Response(ser.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def weekly_attendance_track(request, employee_id=None):
    today_param = request.query_params.get("today")
    start = end = None

    # Parse the optional ?today=YYYY-MM-DD to compute week range
    if today_param:
        try:
            today = datetime.strptime(today_param, "%Y-%m-%d").date()
            weekday = today.weekday()  # Monday=0 .. Sunday=6
            start = today - timedelta(days=weekday)
            end = start + timedelta(days=6)
        except ValueError:
            return Response(
                {"error": "Invalid 'today' format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # Resolve employees to include
    if employee_id:
        try:
            manager = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        # Whatever your helper returns (QuerySet or list), we’ll normalize it
        team_qs = get_emp_under_manager(manager)  # includes subordinates
        # Make sure the manager is included too
        if isinstance(team_qs, Employee.__class__):
            # already a QuerySet
            employees_qs = team_qs | Employee.objects.filter(pk=manager.pk)
        else:
            # assume list/iterable of Employee
            ids = [e.pk for e in team_qs] + [manager.pk]
            employees_qs = Employee.objects.filter(pk__in=ids)
    else:
        employees_qs = Employee.objects.all()

    # Build the biometric filter (week range if provided)
    biometric_filter = Q()
    if start and end:
        biometric_filter &= Q(date__range=(start, end))

    biometric_qs = BiometricData.objects.filter(biometric_filter).order_by("date")

    # Prefetch to a custom attribute so employees with no rows still appear
    employees_qs = employees_qs.prefetch_related(
        Prefetch(
            "biometricdata_set",  # default reverse name; adjust if you set related_name=...
            queryset=biometric_qs,
            to_attr="biometric_entries",
        )
    )

    # Serialize employees; nested list may be empty
    serializer = EmployeeAttendanceSerializer(employees_qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def biometric_weekly_track(request, employee_id=None):
    """
    Returns employees (single or many) with a 7-day 'week' array.
    Each day contains calendar metadata + biometric entry (or null) + leave entry (or null).
    If employee_id is provided, returns only that employee; otherwise returns all active employees for the week.
    Active filter: doj <= week_end AND (resignation_date is null OR resignation_date >= week_start)
    """
    # Parse ?today=YYYY-MM-DD
    today_param = request.query_params.get("today")
    if today_param:
        try:
            today = datetime.strptime(today_param, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid 'today' format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    else:
        today = datetime.now().date()

    start, end = _week_bounds(today)

    # ---- Employee scope ----
    if employee_id:
        # single employee by business key 'employee_id'
        try:
            emp = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)
        employees_qs = Employee.objects.filter(pk=emp.pk)
    else:
        # All employees active in this week
        employees_qs = Employee.objects.filter(
            Q(doj__lte=end)
            & (Q(resignation_date__isnull=True) | Q(resignation_date__gte=start))
        )

    employees = list(
        employees_qs.only("employee_id", "employee_name", "department", "designation")
    )
    if not employees:
        return Response([], status=status.HTTP_200_OK)

    emp_ids = [e.pk for e in employees]

    # ---- Calendar days for the week (7 rows expected) ----
    calendar_days = list(
        Calendar.objects.filter(date__range=(start, end)).order_by("date")
    )
    # (Optional) assert or backfill if needed

    # ---- Data rows for the week ----
    biometric_rows = BiometricData.objects.select_related("employee").filter(
        employee_id__in=emp_ids, date__range=(start, end)
    )
    leave_rows = LeaveDay.objects.select_related("employee").filter(
        employee_id__in=emp_ids, date__range=(start, end)
    )

    # ---- Build lookup maps keyed by (employee_pk, date) ----
    bio_map = {(row.employee_id, row.date): row for row in biometric_rows}
    leave_map = {(row.employee_id, row.date): row for row in leave_rows}

    # ---- Serialize in the same shape as attendance_track ----
    ser = EmployeeWeekSerializer(
        employees,
        many=True,
        context={
            "calendar_days": calendar_days,
            "bio_map": bio_map,
            "leave_map": leave_map,
        },
    )
    return Response(ser.data, status=status.HTTP_200_OK)


# change here
@api_view(["GET"])
def weekly_attendance(request, employee_id=None):

    todaystr = request.query_params.get("today")  # <-- Get the date from filter params
    if todaystr:
        today = datetime.strptime(todaystr, "%Y-%m-%d").date()
    else:
        today = False

    if employee_id:
        try:
            manager = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        employees = get_emp_under_manager(manager)
        print("manager", manager)
        print(employees, "Employees")

        biometric_qs = BiometricData.objects.filter(employee__in=employees)
        manager_biometric_qs = BiometricData.objects.filter(employee=manager)
        biometric_qs = biometric_qs | manager_biometric_qs
        print(biometric_qs, "Biometric qs")
        if today:
            weekday = today.weekday()
            start = today - timedelta(days=weekday)
            end = start + timedelta(days=6)
            calendar_entries = biometric_qs.filter(date__range=(start, end)).order_by(
                "date"
            )

            serializer = BiometricTaskDataSerializer(calendar_entries, many=True)
        else:
            serializer = BiometricTaskDataSerializer(biometric_qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        objs = BiometricData.objects.all()
        if today:
            weekday = today.weekday()
            start = today - timedelta(days=weekday)
            end = start + timedelta(days=6)
            calendar_entries = objs.filter(date__range=(start, end)).order_by("date")

            serializer = BiometricTaskDataSerializer(calendar_entries, many=True)
        else:
            serializer = BiometricTaskDataSerializer(objs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def weekly_attendance_leave(request, employee_id=None):

    todaystr = request.query_params.get("today")  # <-- Get the date from filter params
    if todaystr:
        today = datetime.strptime(todaystr, "%Y-%m-%d").date()
    else:
        today = False

    if employee_id:
        try:
            manager = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        employees = get_emp_under_manager(manager)

        biometric_qs = BiometricData.objects.filter(employee__in=employees)
        if today:
            weekday = today.weekday()
            start = today - timedelta(days=weekday)
            end = start + timedelta(days=6)
            calendar_entries = biometric_qs.filter(date__range=(start, end)).order_by(
                "date"
            )

            serializer = BiometricDataSerializer(calendar_entries, many=True)
        else:
            serializer = BiometricDataSerializer(biometric_qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        objs = BiometricData.objects.all()
        if today:
            weekday = today.weekday()
            start = today - timedelta(days=weekday)
            end = start + timedelta(days=6)
            calendar_entries = objs.filter(date__range=(start, end)).order_by("date")

            serializer = BiometricDataSerializer(calendar_entries, many=True)
        else:
            serializer = BiometricDataSerializer(objs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def attendance_admin(request, employee_id=None):
    if employee_id:
        try:
            manager = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        employees = get_emp_under_manager(manager)

        biometric_qs = BiometricData.objects.filter(employee__in=employees)
        modified_biometric = biometric_qs.filter(modified_by=employee_id)

        serializer = BiometricDataSerializer(modified_biometric, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        objs = BiometricData.objects.all()
        serializer = BiometricDataSerializer(objs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def biometric_daily(request, employee_id=None):

    todaystr = request.query_params.get("today")  # <-- Get the date from filter params
    if todaystr:
        today = datetime.strptime(todaystr, "%Y-%m-%d").date()
    else:
        today = False

    if employee_id:
        biometric_qs = BiometricData.objects.filter(employee=employee_id)
        if today:
            calendar_entries = biometric_qs.filter(date=today)
        else:
            calendar_entries = biometric_qs

        serializer = BiometricDataSerializer(calendar_entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        objs = BiometricData.objects.all()
        serializer = BiometricDataSerializer(objs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def biometric_manager_daily_task(request, manager_id=None):

    todaystr = request.query_params.get("today")  # <-- Get the date from filter params
    if todaystr:
        today = datetime.strptime(todaystr, "%Y-%m-%d").date()
    else:
        today = False

    if manager_id:
        employees = get_emp_under_manager(manager_id)
        # Base queryset filtered by employee list
        base_qs = BiometricData.objects.filter(employee__in=employees)

        # Subquery to get latest biometric entry per employee for the date

        latest_qs = BiometricData.objects.filter(
            employee=OuterRef("employee"),
            date=(
                OuterRef("date") if today else OuterRef("date")
            ),  # generalizes the subquery
        ).order_by("-modified_on")

        biometric_qs = base_qs.filter(pk=Subquery(latest_qs.values("pk")[:1]))

        # biometric_qs = BiometricData.objects.filter(employee__in=employees)

        if today:
            calendar_entries = biometric_qs.filter(date=today)
        else:
            calendar_entries = biometric_qs

        serializer = BiometricTaskDataSerializer(calendar_entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        objs = BiometricData.objects.all()
        serializer = BiometricTaskDataSerializer(objs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def biometric_daily_task(request, employee_id=None):

    todaystr = request.query_params.get("today")  # <-- Get the date from filter params
    if todaystr:
        today = datetime.strptime(todaystr, "%Y-%m-%d").date()
    else:
        today = False

    if employee_id:
        biometric_qs = BiometricData.objects.filter(employee=employee_id)
        if today:
            calendar_entries = biometric_qs.filter(date=today)
        else:
            calendar_entries = biometric_qs

        serializer = BiometricTaskDataSerializer(calendar_entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        objs = BiometricData.objects.all()
        serializer = BiometricTaskDataSerializer(objs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def biometric_weekly_task(request, employee_id=None):

    todaystr = request.query_params.get("today")  # <-- Get the date from filter params
    if todaystr:
        today = datetime.strptime(todaystr, "%Y-%m-%d").date()
    else:
        today = False

    if employee_id:
        biometric_qs = BiometricData.objects.filter(employee=employee_id)
        if today:

            weekday = today.weekday()
            start = today - timedelta(days=weekday)
            end = start + timedelta(days=6)
            calendar_entries = biometric_qs.filter(date__range=(start, end)).order_by(
                "date"
            )
        else:
            calendar_entries = biometric_qs

        serializer = BiometricTaskDataSerializer(calendar_entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        objs = BiometricData.objects.all()
        serializer = BiometricTaskDataSerializer(objs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def bulk_biometric_upload(request):
    data = request.data

    include_holidays = (
        data["holiday"] if isinstance(data.get("holiday"), bool) else False
    )

    # Generate unique group_id
    group_id = generate_group_id(data["employee"])

    # Extract the start and end dates from the payload
    start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
    end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()

    # List to hold valid attendance records
    records = []

    # Loop through the date range and generate records for each valid date
    current_date = start_date
    while current_date <= end_date:
        # Check if the date is a weekend or holiday using the Calendar table
        calendar_data = Calendar.objects.filter(date=current_date).first()

        if (
            not include_holidays
            and calendar_data
            and (calendar_data.is_weekend or calendar_data.is_holiday)
        ):
            # Skip weekend or holiday dates
            current_date += timedelta(days=1)
            continue

        # Add the valid record for the current date
        record = {
            "group_id": group_id,  # Add group_id to each record
            "employee": data["employee"],
            "employee_code": data["employee_code"],
            "employee_name": data["employee_name"],
            "shift": data["shift"],
            "date": current_date,  # Set the current date
            "in_time": data["in_time"],
            "out_time": data["out_time"],
            "work_duration": data["work_duration"],
            "ot": data["ot"],
            "total_duration": data["total_duration"],
            "status": data["status"],
            "remarks": data["remarks"],
            "modified_by": data["modified_by"],
        }
        records.append(record)
        current_date += timedelta(days=1)

    # If no valid records, return an error
    if not records:
        return Response(
            {"error": "No valid attendance dates in the range."}, status=400
        )

    # Serialize and save the valid records
    serializer = BiometricDataSerializer(data=records, many=True)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Bulk biometric data saved successfully"},
            status=status.HTTP_201_CREATED,
        )
    return Response({"details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
