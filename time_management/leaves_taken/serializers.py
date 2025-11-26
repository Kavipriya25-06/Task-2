from rest_framework import serializers
from ..models import LeavesTaken, Employee, Hierarchy, Attachment
from time_management.attachments.serializers import AttachmentSerializer


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "employee_name",
            "last_name",
            "employee_code",
        ]


class HierarchySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hierarchy
        fields = "__all__"


class LeavesTakenSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(
        many=True, source="leaveattachments", read_only=True
    )

    class Meta:
        model = LeavesTaken
        fields = "__all__"


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    approved_by = EmployeeSerializer(read_only=True)
    attachments = AttachmentSerializer(
        many=True, source="leaveattachments", read_only=True
    )

    class Meta:
        model = LeavesTaken
        fields = "__all__"
