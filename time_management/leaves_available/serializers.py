from rest_framework import serializers
from ..models import LeavesAvailable


class LeavesAvailableSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavesAvailable
        fields = "__all__"
