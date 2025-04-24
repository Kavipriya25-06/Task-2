from rest_framework import serializers
from ..models import (
    Task,
    TaskAssign,
    Building,
    BuildingAssign,
    Project,
    ProjectAssign,
    Employee,
)


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class TaskAssignSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Employee.objects.all()
    )

    class Meta:
        model = TaskAssign
        fields = "__all__"


class TaskAndAssignSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)

    class Meta:
        model = TaskAssign
        fields = [
            "task_assign_id",
            "task",
            "task_hours",
            "status",
            "start_date",
            "end_date",
            "employee",
            "building_assign",
        ]


class TaskAndAssignSerializerTest(serializers.ModelSerializer):
    task_assign = TaskAssignSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "task_assign",
            # "task_id",
            "task_title",
            "task_description",
        ]


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class ProjectAssignSerializer(serializers.ModelSerializer):
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


class BuildingAndProjectSerializer(serializers.ModelSerializer):
    building = BuildingSerializer(read_only=True)
    project_assign = ProjectAndAssignSerializer(read_only=True)

    class Meta:
        model = BuildingAssign
        fields = [
            "building_assign_id",
            "building_hours",
            "status",
            "employee",
            "building",
            "project_assign",
        ]


class TaskBuildingSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)
    building_assign = BuildingAndProjectSerializer(read_only=True)

    class Meta:
        model = TaskAssign
        fields = [
            "task_assign_id",
            "task",
            "task_hours",
            "status",
            "start_date",
            "end_date",
            "employee",
            "building_assign",
        ]
