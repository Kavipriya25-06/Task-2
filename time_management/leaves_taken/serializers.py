from rest_framework import serializers
from ..models import LeavesTaken, Employee, Hierarchy


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "employee_name",
            "employee_code",
        ]


class HierarchySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hierarchy
        fields = "__all__"


class LeavesTakenSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavesTaken
        fields = "__all__"


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = LeavesTaken
        fields = [
            "leave_taken_id",
            "leave_type",
            "start_date",
            "end_date",
            "duration",
            "reason",
            "resumption_date",
            "attachment",
            "status",
            "created_at",
            "updated_at",
            "approved_by",
            "employee",
        ]
