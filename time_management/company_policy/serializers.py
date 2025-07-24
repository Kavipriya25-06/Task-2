from rest_framework import serializers
from ..models import CompanyPolicy


class CompanyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyPolicy
        fields = "__all__"
