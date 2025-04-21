from rest_framework import serializers
from ..models import Building, BuildingAssign


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = "__all__"


class BuildingAssignSerializer(serializers.ModelSerializer):
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
