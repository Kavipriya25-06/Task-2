from rest_framework import serializers
from django.db.models import Sum
from django.db.models.functions import TruncWeek, TruncMonth
from ..models import (
    Project,
    ProjectAssign,
    Building,
    BuildingAssign,
    Task,
    TaskAssign,
    Variation,
    TimeSheet,
    Employee,
    LeavesAvailable,
    LeavesTaken,
)

from time_management.project.serializers import (
    VariationSerializer,
)

from time_management.task.serializers import TaskEntrySerializer


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "employee_name",
            "employee_code",
            "doj",
            "status",
            "resignation_date",
        ]


class ProjectAndAssignSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectAssign
        fields = [
            "project_assign_id",
            "status",
        ]


# Task Serializer
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["task_id", "task_code", "task_title", "status"]


# Task Assign Serializer
class TaskAssignSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)

    task_consumed_hours = serializers.SerializerMethodField()

    class Meta:
        model = TaskAssign
        fields = [
            "task_assign_id",
            "status",
            "start_date",
            "task",
            "task_consumed_hours",
        ]

    def get_task_consumed_hours(self, obj):
        total = (
            TimeSheet.objects.filter(task_assign=obj, approved=True).aggregate(
                total=Sum("task_hours")
            )["total"]
            or 0
        )
        return float(total)


# Building Serializer
class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ["building_id", "building_code", "building_title"]


# Building Assign Serializer
class BuildingAssignFullSerializer(serializers.ModelSerializer):
    building = BuildingSerializer(read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = BuildingAssign
        fields = [
            "building_assign_id",
            "status",
            "building",
            "tasks",
        ]

    def get_tasks(self, obj):
        task_assigns = TaskAssign.objects.filter(building_assign=obj)
        return TaskAssignSerializer(task_assigns, many=True).data


# Project Assign Serializer
class ProjectAssignFullSerializer(serializers.ModelSerializer):

    buildings = serializers.SerializerMethodField()

    class Meta:
        model = ProjectAssign
        fields = [
            "project_assign_id",
            "status",
            "buildings",
        ]

    def get_buildings(self, obj):
        building_assigns = BuildingAssign.objects.filter(project_assign=obj)
        return BuildingAssignFullSerializer(building_assigns, many=True).data


# Full Project Serializer
class ProjectHoursSerializer(serializers.ModelSerializer):

    assigns = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "project_id",
            "project_code",
            "project_title",
            "discipline_code",
            "start_date",
            "total_hours",
            "consumed_hours",
            "assigns",
        ]

    def get_assigns(self, obj):
        assigns = ProjectAssign.objects.filter(project=obj)
        return ProjectAssignFullSerializer(assigns, many=True).data

    def get_variation(self, obj):
        variation = Variation.objects.filter(project=obj)
        return VariationSerializer(variation, many=True).data


# weekly Project Serializer
class ProjectWeeklyHoursSerializer(serializers.ModelSerializer):

    task_consumed_hours_by_week = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "project_id",
            "project_code",
            "project_title",
            "discipline_code",
            "start_date",
            "total_hours",
            "consumed_hours",
            "task_consumed_hours_by_week",
        ]

    def get_task_consumed_hours_by_week(self, obj):
        # Group timesheet entries by week and sum approved hours
        qs = (
            TimeSheet.objects.filter(
                task_assign__building_assign__project_assign__project=obj, approved=True
            )
            .annotate(week=TruncWeek("date"))
            .values("week")
            .annotate(total=Sum("task_hours"))
            .order_by("week")
        )
        return [
            {
                "week": (
                    entry["week"].strftime("%Y-W%U") if entry["week"] else "Unknown"
                ),
                "hours": float(entry["total"]),
            }
            for entry in qs
        ]


# Monthly Project Serializer
class ProjectMonthlyHoursSerializer(serializers.ModelSerializer):

    task_consumed_hours_by_month = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "project_id",
            "project_code",
            "project_title",
            "discipline_code",
            "start_date",
            "total_hours",
            "consumed_hours",
            "task_consumed_hours_by_month",
        ]

    def get_task_consumed_hours_by_month(self, obj):
        # Group timesheet entries by week and sum approved hours
        qs = (
            TimeSheet.objects.filter(
                task_assign__building_assign__project_assign__project=obj, approved=True
            )
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total=Sum("task_hours"))
            .order_by("month")
        )
        return [
            {
                "month": (
                    entry["month"].strftime("%Y-%m") if entry["month"] else "Unknown"
                ),
                "hours": float(entry["total"]),
            }
            for entry in qs
        ]


class TimeSheetTaskSerializer(serializers.ModelSerializer):
    task_assign = TaskEntrySerializer(read_only=True)
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = TimeSheet
        fields = "__all__"


class LeavesAvailableSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = LeavesAvailable
        fields = "__all__"


class EmployeeLOPSerializer(serializers.ModelSerializer):

    lop_by_month = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "employee_name",
            "employee_code",
            "doj",
            "status",
            "resignation_date",
            "lop_by_month",
        ]

    def get_lop_by_month(self, obj):

        qs = (
            LeavesTaken.objects.filter(employee=obj)
            .annotate(month=TruncMonth("start_date"))
            .values("month")
            .annotate(total=Sum("duration"))
            .order_by("month")
        )
        return [
            {
                "month": (
                    entry["month"].strftime("%Y-%m") if entry["month"] else "Unknown"
                ),
                "days": float(entry["total"]),
            }
            for entry in qs
        ]
