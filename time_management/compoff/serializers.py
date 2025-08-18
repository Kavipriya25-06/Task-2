from rest_framework import serializers
from django.db.models import Sum
from ..models import Calendar, CompOffRequest, Employee, TimeSheet, CompOffExpiry
from time_management.time_sheet.serializers import TimeSheetTaskSerializer


class CompOffRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompOffRequest
        fields = "__all__"


class CompOffExpirySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompOffExpiry
        fields = "__all__"


class TimeSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSheet
        fields = "__all__"


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["employee_id", "employee_code", "employee_name"]


class CompOffRequestEmployeeSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer()

    class Meta:
        model = CompOffRequest
        fields = "__all__"


class CompOffRequestTaskSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer()
    timesheets = serializers.SerializerMethodField()
    timesheet_count = serializers.SerializerMethodField()
    task_hours_sum = serializers.SerializerMethodField()

    class Meta:
        model = CompOffRequest
        fields = [
            "compoff_request_id",
            "date",
            "duration",
            "reason",
            "expiry_date",
            "status",
            "created_at",
            "updated_at",
            "employee",
            "approved_by",
            "timesheets",
            "timesheet_count",
            "task_hours_sum",
        ]

    def get_timesheets(self, obj):
        timesheets = TimeSheet.objects.filter(employee=obj.employee, date=obj.date)
        return TimeSheetTaskSerializer(timesheets, many=True).data

    def get_timesheet_count(self, obj):
        return TimeSheet.objects.filter(employee=obj.employee, date=obj.date).count()

    def get_task_hours_sum(self, obj):

        return (
            TimeSheet.objects.filter(employee=obj.employee, date=obj.date).aggregate(
                total=Sum("task_hours")
            )["total"]
            or 0.0
        )
