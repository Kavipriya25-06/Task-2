from rest_framework.viewsets import ModelViewSet
from ..models import BiometricData, Employee, TimeSheet
from time_management.biometric.serializers import BiometricDataSerializer
from time_management.time_sheet.serializers import (
    TimeSheetDataSerializer,
    TimeSheetTaskSerializer,
)
from time_management.hierarchy.serializers import emp_under_manager
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.db.models import Sum


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def timesheet_data_api(request, timesheet_id=None):
    if request.method == "GET":
        if timesheet_id:
            try:
                obj = TimeSheet.objects.get(timesheet_id=timesheet_id)
                serializer = TimeSheetDataSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except TimeSheet.DoesNotExist:
                return Response(
                    {"error": "TimeSheetData record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = TimeSheet.objects.all()
            serializer = TimeSheetDataSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = TimeSheetDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "TimeSheetData record added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not timesheet_id:
            return Response(
                {"error": "TimeSheetData ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = TimeSheet.objects.get(timesheet_id=timesheet_id)
        except TimeSheet.DoesNotExist:
            return Response(
                {"error": "TimeSheetData record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TimeSheetDataSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "TimeSheetData record updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not timesheet_id:
            return Response(
                {"error": "TimeSheetData ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = TimeSheet.objects.get(timesheet_id=timesheet_id)
            obj.delete()
            return Response(
                {"message": "TimeSheetData record deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except TimeSheet.DoesNotExist:
            return Response(
                {"error": "TimeSheetData record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["GET"])
def timesheet_under_manager(request, employee_id=None):
    if employee_id:
        try:
            manager = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        employees = emp_under_manager(manager)

        timesheet_qs = TimeSheet.objects.filter(employee__in=employees)

        serializer = TimeSheetTaskSerializer(timesheet_qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        objs = TimeSheet.objects.all()
        serializer = TimeSheetTaskSerializer(objs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def manager_weekly_timesheet(request, employee_id=None):

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

        employees = emp_under_manager(manager)

        timesheet_qs = TimeSheet.objects.filter(employee__in=employees)
        if today:
            weekday = today.weekday()
            start = today - timedelta(days=weekday)
            end = start + timedelta(days=6)
            timesheet_entries = timesheet_qs.filter(date__range=(start, end)).order_by(
                "date"
            )

            serializer = TimeSheetTaskSerializer(timesheet_entries, many=True)
        else:
            serializer = TimeSheetTaskSerializer(timesheet_qs, many=True)

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
def manager_daily_timesheet(request, employee_id=None):

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

        employees = emp_under_manager(manager)

        timesheet_qs = TimeSheet.objects.filter(employee__in=employees)
        if today:
            # weekday = today.weekday()
            # start = today - timedelta(days=weekday)
            # end = start + timedelta(days=6)
            # timesheet_entries = timesheet_qs.filter(date__range=(start, end)).order_by(
            #     "date"
            # )
            timesheet_entries = timesheet_qs.filter(date=today)

            serializer = TimeSheetTaskSerializer(timesheet_entries, many=True)
        else:
            serializer = TimeSheetTaskSerializer(timesheet_qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        objs = TimeSheet.objects.all()
        if today:
            # weekday = today.weekday()
            # start = today - timedelta(days=weekday)
            # end = start + timedelta(days=6)
            # timesheet_entries = objs.filter(date__range=(start, end)).order_by("date")
            timesheet_entries = timesheet_qs.filter(date=today)

            serializer = TimeSheetTaskSerializer(timesheet_entries, many=True)
        else:
            serializer = TimeSheetTaskSerializer(objs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def employee_weekly_timesheet(request, employee_id=None):

    todaystr = request.query_params.get("today")  # <-- Get the date from filter params
    if todaystr:
        today = datetime.strptime(todaystr, "%Y-%m-%d").date()
    else:
        today = False

    if employee_id:
        try:
            employee_timesheet = TimeSheet.objects.filter(employee=employee_id)
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
def employee_daily_timesheet(request, employee_id=None):

    todaystr = request.query_params.get("today")  # <-- Get the date from filter params
    if todaystr:
        today = datetime.strptime(todaystr, "%Y-%m-%d").date()
    else:
        today = False

    if employee_id:
        try:
            # manager = Employee.objects.get(employee_id=employee_id)
            employee_timesheet = TimeSheet.objects.filter(employee=employee_id)
        except TimeSheet.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        # employees = emp_under_manager(manager)

        if today:
            # weekday = today.weekday()
            # start = today - timedelta(days=weekday)
            # end = start + timedelta(days=6)
            # timesheet_entries = employee_timesheet.filter(date__range=(start, end)).order_by(
            #     "date"
            # )
            timesheet_entries = employee_timesheet.filter(date=today)

            serializer = TimeSheetTaskSerializer(timesheet_entries, many=True)
        else:
            serializer = TimeSheetTaskSerializer(employee_timesheet, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        objs = TimeSheet.objects.all()
        if today:
            # weekday = today.weekday()
            # start = today - timedelta(days=weekday)
            # end = start + timedelta(days=6)
            timesheet_entries = objs.filter(date=today)

            serializer = TimeSheetTaskSerializer(timesheet_entries, many=True)
        else:
            serializer = TimeSheetTaskSerializer(objs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def total_logged_hours(request, project_id=None, building_id=None, task_id=None):

    total_hours = 0
    if project_id:
        total_hours = (
            TimeSheet.objects.filter(
                task_assign__building_assign__project_assign__project__project_id=project_id,
            ).aggregate(total_hours=Sum("task_hours"))["total_hours"]
            or 0
        )

    if building_id:
        total_hours = (
            TimeSheet.objects.filter(
                task_assign__building_assign__building__building_id=building_id,
            ).aggregate(total_hours=Sum("task_hours"))["total_hours"]
            or 0
        )

    if task_id:
        total_hours = (
            TimeSheet.objects.filter(
                task_assign__task__task_id=task_id,
            ).aggregate(
                total_hours=Sum("task_hours")
            )["total_hours"]
            or 0
        )

    # Filter timesheets by navigating the relationships
    # total_hours = (
    #     TimeSheet.objects.filter(
    #         task_assign__task__task_id=task_id,
    #         task_assign__building_assign__building__building_id=building_id,
    #         task_assign__building_assign__project_assign__project__project_id=project_id,
    #     ).aggregate(total_hours=Sum("task_hours"))["total_hours"]
    #     or 0
    # )

    return Response({"total_logged_hours": total_hours})



