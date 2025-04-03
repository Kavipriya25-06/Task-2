from rest_framework import serializers
from ..models import Employee, Hierarchy, User


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["user_id", "email", "role"]


class HierarchySerializer(serializers.ModelSerializer):

    class Meta:
        model = Hierarchy
        fields = ["hierarchy_id", "reporting_to"]


class EmployeeViewSerializer(serializers.ModelSerializer):

    user_details = UserSerializer(many=True, read_only=True, source="user_set")
    hierarchy_details = HierarchySerializer(
        many=True, read_only=True, source="hierarchy_set"
    )

    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "employee_name",
            "employee_code",
            "status",
            "designation",
            "department",
            "user_details",
            "hierarchy_details",
        ]
