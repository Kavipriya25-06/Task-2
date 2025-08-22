from rest_framework import serializers
from ..models import (
    Project,
    ProjectAssign,
    AreaOfWork,
    Discipline,
    Employee,
    BuildingAssign,
    TaskAssign,
    Building,
    Task,
    Variation,
)

from time_management.building.serializers import BuildingAndProjectSerializer
from time_management.attachments.serializers import AttachmentSerializer
from time_management.variations.serializers import VariationSerializer


class ProjectSerializer(serializers.ModelSerializer):
    # area_of_work = serializers.PrimaryKeyRelatedField(
    #     queryset=AreaOfWork.objects.all(), many=True
    # )
    attachments = AttachmentSerializer(
        many=True, source="Projectattachments", read_only=True
    )

    class Meta:
        model = Project
        fields = "__all__"


class ProjectAssignSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Employee.objects.all()
    )

    class Meta:
        model = ProjectAssign
        fields = "__all__"


class ProjectAndAssignSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = ProjectAssign
        fields = [
            "project_assign_id",
            "project_hours",
            "status",
            "employee",
            "project",
        ]


class AreaOfWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaOfWork
        fields = "__all__"


class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discipline
        fields = "__all__"


# Employee Basic Serializer
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["employee_id", "employee_name", "designation"]


# Task Serializer
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


# Task Assign Serializer
class TaskAssignSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)
    employee = EmployeeSerializer(many=True, read_only=True)

    class Meta:
        model = TaskAssign
        fields = "__all__"


# Building Serializer
class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = "__all__"


# Building Assign Serializer
class BuildingAssignFullSerializer(serializers.ModelSerializer):
    building = BuildingSerializer(read_only=True)
    employee = EmployeeSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()
    project_assign = ProjectAndAssignSerializer(read_only=True)

    class Meta:
        model = BuildingAssign
        fields = [
            "building_assign_id",
            "building_hours",
            "status",
            "employee",
            "building",
            "tasks",
            "project_assign",
        ]

    def get_tasks(self, obj):
        task_assigns = TaskAssign.objects.filter(building_assign=obj)
        return TaskAssignSerializer(task_assigns, many=True).data


# Project Assign Serializer
class ProjectAssignFullSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(many=True, read_only=True)
    buildings = serializers.SerializerMethodField()

    class Meta:
        model = ProjectAssign
        fields = [
            "project_assign_id",
            "project_hours",
            "status",
            "employee",
            "buildings",
        ]

    def get_buildings(self, obj):
        building_assigns = BuildingAssign.objects.filter(project_assign=obj)
        return BuildingAssignFullSerializer(building_assigns, many=True).data


# Full Project Serializer
class ProjectFullSerializer(serializers.ModelSerializer):
    # area_of_work = serializers.SlugRelatedField(
    #     slug_field="area_name", many=True, read_only=True
    # )
    created_by = EmployeeSerializer(read_only=True)
    assigns = serializers.SerializerMethodField()
    variation = serializers.SerializerMethodField()
    attachments = AttachmentSerializer(
        many=True, source="Projectattachments", read_only=True
    )

    class Meta:
        model = Project
        fields = [
            "project_id",
            "project_title",
            "project_type",
            "start_date",
            "due_date",
            "completed_status",
            "estimated_hours",
            "variation_hours",
            "client",
            "total_hours",
            "consumed_hours",
            "project_description",
            "project_code",
            "discipline_code",
            "discipline",
            "status",
            "created_at",
            "updated_at",
            "created_by",
            "assigns",
            "attachments",
            "variation",
        ]

    def get_assigns(self, obj):
        assigns = ProjectAssign.objects.filter(project=obj)
        return ProjectAssignFullSerializer(assigns, many=True).data

    def get_variation(self, obj):
        variation = Variation.objects.filter(project=obj)
        return VariationSerializer(variation, many=True).data
