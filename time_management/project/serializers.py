from rest_framework import serializers
from ..models import Project, ProjectAssign


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
