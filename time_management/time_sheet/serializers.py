from rest_framework import serializers
from ..models import BiometricData, TimeSheet
from time_management.task.serializers import TaskEntrySerializer


class BiometricDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiometricData
        fields = "__all__"


class TimeSheetDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSheet
        fields = "__all__"


class TimeSheetTaskSerializer(serializers.ModelSerializer):
    task_assign = TaskEntrySerializer(read_only=True)

    class Meta:
        model = TimeSheet
        fields = "__all__"
