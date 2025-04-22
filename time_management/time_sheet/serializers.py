from rest_framework import serializers
from ..models import BiometricData, TimeSheet


class BiometricDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiometricData
        fields = "__all__"


class TimeSheetDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSheet
        fields = "__all__"
