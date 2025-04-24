from rest_framework import serializers
from ..models import Building, BuildingAssign, Project, ProjectAssign, Employee


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = "__all__"


class BuildingAssignSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Employee.objects.all()
    )

    class Meta:
        model = BuildingAssign
        fields = "__all__"


class BuildingAndAssignSerializer(serializers.ModelSerializer):
    building = BuildingSerializer(read_only=True)

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
