from rest_framework import serializers
from ..models import User, Employee


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "employee_name",
            "employee_code",
            "status",
            "designation",
            "department",
        ]


class UserDetailsSerializer(serializers.ModelSerializer):
    employee_id = EmployeeSerializer(
        read_only=True,
    )

    class Meta:
        model = User
        fields = ["user_id", "email", "password", "role", "employee_id", "status"]
