from rest_framework.viewsets import ModelViewSet
import uuid
from django.db.models import OuterRef, Subquery
from ..models import BiometricData, Employee, Calendar
from time_management.biometric.serializers import (
    BiometricDataSerializer,
    BiometricTaskDataSerializer,
)
from time_management.hierarchy.serializers import (
    emp_under_manager,
    get_emp_under_manager,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from datetime import datetime, timedelta
from django.http import JsonResponse


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

        if calendar_data and (calendar_data.is_weekend or calendar_data.is_holiday):
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
