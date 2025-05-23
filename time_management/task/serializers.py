from rest_framework import serializers
from ..models import (
    Task,
    TaskAssign,
    Building,
    BuildingAssign,
    Project,
    ProjectAssign,
    Employee,
    Attachment,
)
from time_management.attachments.serializers import AttachmentSerializer
from time_management.project.serializers import EmployeeSerializer


class TaskSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(
        many=True, source="Taskattachments", read_only=True
    )

    class Meta:
        model = Task
        fields = "__all__"

        def validate_task_code(self, value):

            if value and Task.objects.filter(task_code=value).exists():
                if self.instance and self.instance.task_code == value:
                    return value  # Allow if it's the same record
                raise serializers.ValidationError("Task code already exists")
            return value


class TaskAssignSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Employee.objects.all()
    )
    attachments = AttachmentSerializer(
        many=True, source="TaskAssignattachments", read_only=True
    )

    class Meta:
        model = TaskAssign
        fields = "__all__"


class TaskAndAssignSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)
    attachments = AttachmentSerializer(
        many=True, source="TaskAssignattachments", read_only=True
    )

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
            "attachments",
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
    employee = EmployeeSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(
        many=True, source="TaskAssignattachments", read_only=True
    )

    class Meta:
        model = TaskAssign
        fields = [
            "task_assign_id",
            "priority",
            "task",
            "task_hours",
            "status",
            "start_date",
            "end_date",
            "employee",
            "building_assign",
            "comments",
            "attachments",
        ]


class TaskViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ["task_id", "task_title", "task_code"]


class BuildingTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ["building_id", "building_title", "building_code"]


class ProjectTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["project_id", "project_title", "project_code"]


class ProjectViewSerializer(serializers.ModelSerializer):
    project = ProjectTaskSerializer(read_only=True)

    class Meta:
        model = ProjectAssign
        fields = [
            "project_assign_id",
            # "project_hours",
            # "status",
            # "employee",
            "project",
        ]


class BuildingViewSerializer(serializers.ModelSerializer):
    building = BuildingTaskSerializer(read_only=True)
    project_assign = ProjectViewSerializer(read_only=True)

    class Meta:
        model = BuildingAssign
        fields = [
            "building_assign_id",
            # "building_hours",
            # "status",
            # "employee",
            "building",
            "project_assign",
        ]


class TaskEntrySerializer(serializers.ModelSerializer):
    task = TaskViewSerializer(read_only=True)
    building_assign = BuildingViewSerializer(read_only=True)
    # employee = EmployeeSerializer(many=True, read_only=True)

    class Meta:
        model = TaskAssign
        fields = [
            "task_assign_id",
            "task",
            # "task_hours",
            # "status",
            # "start_date",
            # "end_date",
            # "employee",
            "building_assign",
        ]
