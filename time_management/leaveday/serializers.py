from rest_framework import serializers
from ..models import Employee, LeaveDay


class EmployeeLongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "employee_name",
            "employee_code",
            "doj",
            "status",
            "resignation_date",
            "department",
        ]


class LeaveDaySerializer(serializers.ModelSerializer):
    employee = EmployeeLongSerializer(read_only=True)

    class Meta:
        model = LeaveDay
        fields = "__all__"
