from rest_framework import serializers
from ..models import Modifications, Employee

# from time_management.employee.serializers import EmployeeListSerializer


class EmployeeListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "employee_name",
            "employee_code",
            "employee_email",
            "status",
            "designation",
            "department",
        ]


class ModificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modifications
        fields = "__all__"


class ModificationsEmployeeSerializer(serializers.ModelSerializer):

    modified_by = EmployeeListSerializer()

    class Meta:
        model = Modifications
        fields = "__all__"
