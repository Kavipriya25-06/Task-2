from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Sum, Q

import csv
import io
from datetime import datetime
from django.http import HttpResponse
from django.db import connection
from datetime import datetime, timedelta, date


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
)
from time_management.project.serializers import ProjectSerializer
from time_management.building.serializers import BuildingAndAssignSerializer
from time_management.leaves_taken.serializers import (
    LeavesTakenSerializer,
    LeaveRequestSerializer,
)


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
def year_leaves(request):
    year = request.query_params.get("year")
    try:
        if year:
            yearly_leaves = LeavesTaken.objects.filter(start_date__year=year).order_by(
                "start_date"
            )
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
    if request.method == "GET":
        try:
            obj = LeavesAvailable.objects.all()
            serializer = LeavesAvailableSerializer(obj, many=True)
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
                employees, many=True, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
            )
