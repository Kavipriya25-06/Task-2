from rest_framework import serializers
from ..models import LeavesAvailable, CompOff


class LeavesAvailableSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavesAvailable
        fields = "__all__"


class CompOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompOff
        fields = "__all__"
