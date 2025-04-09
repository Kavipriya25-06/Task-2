from rest_framework import serializers
from ..models import (
    Project,
    ProjectAssign,
    Building,
    BuildingAssign,
    Task,
    TaskAssign,
    Hierarchy,
    Employee,
    User,
)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"


class HierarchySerializer(serializers.ModelSerializer):

    class Meta:
        model = Hierarchy
        fields = "__all__"


# Serializer for Task Model
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


# Serializer for Building Model
class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = "__all__"


# Serializer for Task Assignment Model
class TaskAssignSerializer(serializers.ModelSerializer):
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
        ]


# Serializer for Building Assignment Model
class BuildingAssignSerializer(serializers.ModelSerializer):
    building = BuildingSerializer(read_only=True)
    task_assigns = TaskAssignSerializer(many=True, read_only=True)

    class Meta:
        model = BuildingAssign
        fields = [
            "building_assign_id",
            "building",
            "building_hours",
            "status",
            "task_assigns",
        ]


class ProjectAssignSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)  # This will include project details
    building_assigns = BuildingAssignSerializer(many=True, read_only=True)
    task_assigns = TaskAssignSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectAssign
        fields = [
            "project_assign_id",
            "project",  # Add the project field here
            "project_hours",
            "status",
            "building_assigns",
            "task_assigns",
        ]


# Serializer for Project Model (with assigned projects)
class ProjectViewSerializer(serializers.ModelSerializer):
    project_assignments = ProjectAssignSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ["project_id", "project_title", "project_code", "project_assignments"]


# class ProjectAssignSerializer(serializers.ModelSerializer):
#     building_assigns = BuildingAssignSerializer(many=True, read_only=True)
#     task_assigns = TaskAssignSerializer(many=True, read_only=True)

#     class Meta:
#         model = ProjectAssign
#         fields = [
#             "project_assign_id",
#             "project_hours",
#             "status",
#             "building_assigns",
#             "task_assigns",
#         ]


# Serializer for Project Assignment Model
# class ProjectAssignSerializer(serializers.ModelSerializer):
#     # project = (
#     #     serializers.StringRelatedField()
#     # )  # to show project title or you can define a ProjectSerializer if needed
#     building_assigns = BuildingAssignSerializer(many=True, read_only=True)
#     task_assigns = TaskAssignSerializer(many=True, read_only=True)

#     class Meta:
#         model = ProjectAssign
#         fields = [
#             "project_assign_id",
#             # "project",
#             "project_hours",
#             "status",
#             "building_assigns",
#             "task_assigns",
#         ]


# class ProjectAssignSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProjectAssign
#         fields = "__all__"
