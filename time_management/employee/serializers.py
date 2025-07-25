from rest_framework import serializers
from ..models import (
    Employee,
    Hierarchy,
    User,
    Attachment,
    Modifications,
    LanguagesKnown,
    Education,
    Dependant,
    WorkExperience,
    Assets,
    EmployeeAttachment,
)
from time_management.attachments.serializers import AttachmentSerializer
from time_management.employee_attachment.serializers import EmployeeAttachmentSerializer
from time_management.modifications.serializers import ModificationsSerializer
from time_management.languagesknown.serializers import LanguagesKnownSerializer
from time_management.education.serializers import EducationSerializer
from time_management.dependant.serializers import DependantSerializer
from time_management.workexperience.serializers import WorkExperienceSerializer
from time_management.assets.serializers import AssetsSerializer


class EmployeeSerializer(serializers.ModelSerializer):
    attachments = EmployeeAttachmentSerializer(
        many=True, source="Employeedetailsattachments", read_only=True
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


class EmployeeAllSerializer(serializers.ModelSerializer):
    attachments = EmployeeAttachmentSerializer(
        many=True, source="Employeedetailsattachments", read_only=True
    )
    added_by = serializers.SerializerMethodField()
    last_modified_by = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    languages_known = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    dependant = serializers.SerializerMethodField()
    work_experience = serializers.SerializerMethodField()
    assets = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "attachments",
            "employee_code",
            "employee_name",
            "last_name",
            "fathers_name",
            "gender",
            "dob",
            "age",
            "doj",
            "contact_number",
            "identification_marks",
            "wedding_date",
            "marital_status",
            "personal_email",
            "aadhaar_number",
            "PAN",
            "UAN",
            "pf_number",
            "esi_number",
            "passport_number",
            "passport_validity",
            "onboarding_status",
            "status",
            "remarks",
            "location",
            "permanent_address",
            "local_address",
            "employment_type",
            "designation",
            "source_of_hire",
            "department",
            "qualification",
            "year_of_passing",
            "previous_company_name",
            "previous_experience",
            "aero360_experience",
            "total_experience",
            "experience_in_years",
            "probation_confirmation_date",
            "contract_end_date",
            "employee_email",
            "reporting_manager",
            "second_reporting_manager",
            "resignation_date",
            "relieving_date",
            "seating_location",
            "work_phone",
            "extension",
            "account_number",
            "ifsc_code",
            "bank_name",
            "bank_branch_name",
            "bank_address",
            "emergency_contact_name",
            "emergency_contact_relationship",
            "emergency_contact_number",
            "blood_group",
            "created_at",
            "updated_at",
            "profile_picture",
            "attachments",
            "added_by",
            "last_modified_by",
            "role",
            "languages_known",
            "education",
            "dependant",
            "work_experience",
            "assets",
        ]

    def get_added_by(self, obj):
        try:
            modifications = Modifications.objects.filter(
                employee=obj.employee_id
            ).first()
            return ModificationsSerializer(modifications).data
        except Modifications.DoesNotExist:
            return None

    def get_last_modified_by(self, obj):
        try:
            modifications = Modifications.objects.filter(
                employee=obj.employee_id
            ).last()
            return ModificationsSerializer(modifications).data
        except Modifications.DoesNotExist:
            return None

    def get_role(self, obj):
        try:
            role = User.objects.get(employee_id=obj.employee_id)
            return role.role
        except User.DoesNotExist:
            return None

    def get_languages_known(self, obj):
        try:
            languages = LanguagesKnown.objects.filter(employee=obj.employee_id)
            return LanguagesKnownSerializer(languages, many=True).data
        except LanguagesKnown.DoesNotExist:
            return None

    def get_education(self, obj):
        try:
            education = Education.objects.filter(employee=obj.employee_id)
            return EducationSerializer(education, many=True).data
        except Education.DoesNotExist:
            return None

    def get_dependant(self, obj):
        try:
            dependant = Dependant.objects.filter(employee=obj.employee_id)
            return DependantSerializer(dependant, many=True).data
        except Dependant.DoesNotExist:
            return None

    def get_work_experience(self, obj):
        try:
            work_experience = WorkExperience.objects.filter(employee=obj.employee_id)
            return WorkExperienceSerializer(work_experience, many=True).data
        except WorkExperience.DoesNotExist:
            return None

    def get_assets(self, obj):
        try:
            assets = Assets.objects.filter(employee=obj.employee_id)
            return AssetsSerializer(assets, many=True).data
        except Assets.DoesNotExist:
            return None
