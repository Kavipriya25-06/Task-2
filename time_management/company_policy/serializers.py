from rest_framework import serializers
from ..models import CompanyPolicy
from time_management.employee.serializers import EmployeeViewSerializer


class CompanyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyPolicy
        fields = "__all__"


class CompanyPolicyViewSerializer(serializers.ModelSerializer):
    uploaded_by = EmployeeViewSerializer(
        read_only=True,
    )

    class Meta:
        model = CompanyPolicy
        fields = "__all__"
