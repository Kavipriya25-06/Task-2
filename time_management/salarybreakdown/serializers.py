from rest_framework import serializers
from ..models import SalaryBreakdown


class SalaryBreakdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryBreakdown
        fields = "__all__"
