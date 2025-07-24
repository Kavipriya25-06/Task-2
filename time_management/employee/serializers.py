from rest_framework import serializers
from ..models import Employee, Hierarchy, User, Attachment
from time_management.attachments.serializers import AttachmentSerializer
from time_management.employee_attachment.serializers import EmployeeAttachmentSerializer


class EmployeeSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(
        many=True, source="Employeeattachments", read_only=True
    )

    class Meta:
        model = Employee
        fields = "__all__"

        def validate_employee_email(self, value):

            if value and Employee.objects.filter(employee_email=value).exists():
                if self.instance and self.instance.employee_email == value:
                    return value  # Allow if it's the same record
                raise serializers.ValidationError("Email already exists")
            return value

        def validate_personal_email(self, value):

            if value and Employee.objects.filter(personal_email=value).exists():
                if self.instance and self.instance.personal_email == value:
                    return value  # Allow if it's the same record
                raise serializers.ValidationError("Email already exists")
            return value


class ManagerSerializer(serializers.ModelSerializer):
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
            "employee_email",
            "status",
            "designation",
            "department",
            "user_details",
            "hierarchy_details",
        ]


class HierarchyManagerSerializer(serializers.ModelSerializer):

    reporting_to = ManagerSerializer(
        read_only=True,
    )

    class Meta:
        model = Hierarchy
        fields = ["hierarchy_id", "reporting_to"]


class EmployeeListSerializer(serializers.ModelSerializer):

    user_details = UserSerializer(many=True, read_only=True, source="user_set")
    hierarchy_details = HierarchyManagerSerializer(
        many=True, read_only=True, source="hierarchy_set"
    )
    # reporting_manager = serializers.SerializerMethodField()
    # ManagerSerializer(many=True, read_only=True, source="user_set")

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
            "user_details",
            "hierarchy_details",
            # "reporting_manager",
        ]

    # def get_reporting_manager(self, obj):
    #     manager = Employee.objects.filter(reporting_manager=obj)
    #     return ManagerSerializer(manager, many=True).data
