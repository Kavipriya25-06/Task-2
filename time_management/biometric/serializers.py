from rest_framework import serializers
from ..models import BiometricData, Calendar, TaskAssign, TimeSheet
from time_management.time_sheet.serializers import (
    TimeSheetTaskSerializer,
)


class BiometricDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiometricData
        fields = "__all__"


class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = ["calendar_id", "date", "is_weekend", "is_holiday"]


class BiometricTaskDataSerializer(serializers.ModelSerializer):
    calendar = serializers.SerializerMethodField()
    timesheets = serializers.SerializerMethodField()
    leave_deduction = serializers.SerializerMethodField()

    class Meta:
        model = BiometricData
        fields = [
            "biometric_id",
            "employee_code",
            "employee_name",
            "shift",
            "date",
            "in_time",
            "out_time",
            "work_duration",
            "ot",
            "total_duration",
            "status",
            "remarks",
            "modified_on",
            "employee",
            "modified_by",
            "calendar",
            "timesheets",
            "leave_deduction",
        ]

    def get_calendar(self, obj):
        try:
            calendar = Calendar.objects.get(date=obj.date)
            return CalendarSerializer(calendar).data
        except Calendar.DoesNotExist:
            return None

    def get_timesheets(self, obj):
        try:
            timesheets = TimeSheet.objects.filter(employee=obj.employee, date=obj.date)
            return TimeSheetTaskSerializer(timesheets, many=True).data
        except TimeSheet.DoesNotExist:
            return None

    def get_leave_deduction(self, obj):
        from time_management.leaves_available.views import get_comp_off

        print("Object", obj)
        try:
            return get_comp_off(float(obj.total_duration or 0))
        except:
            return 0
