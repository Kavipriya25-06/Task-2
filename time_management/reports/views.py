from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Sum

import csv
import io
from datetime import datetime
from django.http import HttpResponse
from django.db import connection


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
)

from time_management.reports.serializers import (
    ProjectHoursSerializer,
    ProjectWeeklyHoursSerializer,
    ProjectMonthlyHoursSerializer,
)
from time_management.project.serializers import ProjectSerializer
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
