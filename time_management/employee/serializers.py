from rest_framework import serializers
from ..models import Employee, Hierarchy, User, Attachment
from time_management.attachments.serializers import AttachmentSerializer


class EmployeeSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(
        many=True, source="Employeeattachments", read_only=True
    )

    class Meta:
        model = Employee
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["user_id", "email", "role", "status"]


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
