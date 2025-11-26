from rest_framework import serializers
from ..models import (
    BiometricData,
    Calendar,
    TaskAssign,
    TimeSheet,
    LeavesTaken,
    LeaveDay,
    Employee,
)
from time_management.time_sheet.serializers import (
    TimeSheetTaskSerializer,
)
from time_management.leaves_taken.serializers import (
    LeavesTakenSerializer,
    LeaveRequestSerializer,
)
from time_management.leaveday.serializers import LeaveDaySerializer


class EmployeeNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = (
            "employee_id",
            "employee_code",
            "employee_name",
            "last_name",
            "department",
            "designation",
        )


class BiometricDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiometricData
        fields = "__all__"


class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = ["calendar_id", "date", "is_weekend", "is_holiday"]


class CalendarMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = (
            "calendar_id",
            "date",
            "day_name",
            "day_of_week",
            "is_weekend",
            "is_holiday",
            "notes",
            "month",
            "month_name",
            "week_of_year",
        )


class BiometricAttendanceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiometricData
        fields = "__all__"


class BiometricTaskDataSerializer(serializers.ModelSerializer):
    calendar = serializers.SerializerMethodField()
    leaveday = serializers.SerializerMethodField()
    timesheets = serializers.SerializerMethodField()
    leave_deduction = serializers.SerializerMethodField()

    employee_names = serializers.SerializerMethodField()

    class Meta:
        model = BiometricData
        fields = [
            "biometric_id",
            "employee_code",
            "employee_name",
            "employee_names",
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
            "leaveday",
            "leave_deduction",
        ]

    def get_leaveday(self, obj):
        try:
            leave = LeaveDay.objects.filter(
                employee=obj.employee, date=obj.date
            ).first()
            return LeaveDaySerializer(leave).data
        except LeaveDay.DoesNotExist:
            return None

    def get_calendar(self, obj):
        try:
            calendar = Calendar.objects.get(date=obj.date)
            return CalendarMiniSerializer(calendar).data
        except Calendar.DoesNotExist:
            return None

    def get_employee_names(self, obj):
        try:
            employee_names = Employee.objects.get(employee_id=obj.employee)
            return EmployeeNameSerializer(employee_names).data
        except Employee.DoesNotExist:
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


# class AttendanceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Calendar
#         fields = ["calendar_id", "date", "is_weekend", "is_holiday"]


class EmployeeAttendanceSerializer(serializers.ModelSerializer):
    # We’ll attach prefetched rows to `employee.biometric_entries`
    biometric_entries = BiometricTaskDataSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = (
            "employee_id",
            "employee_code",
            "employee_name",
            "department",
            "designation",
            # any other Employee fields you want to return...
            "biometric_entries",
        )


class EmployeeWeekSerializer(serializers.ModelSerializer):
    week = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = (
            "employee_id",
            "employee_name",
            "department",
            "designation",
            "last_name",
            # add any other Employee fields you want
            "week",
        )

    def get_week(self, employee):
        """
        Build a 7-day list from the provided calendar days,
        attaching biometric/leave for (employee, date) or None.
        """
        cal_days = self.context["calendar_days"]  # list[Calendar]
        bio_map = self.context["bio_map"]  # dict[(emp_pk, date)]=BiometricData
        leave_map = self.context["leave_map"]  # dict[(emp_pk, date)]=LeaveDay

        out = []
        for cal in cal_days:
            key = (employee.pk, cal.date)
            biometric = bio_map.get(key)
            leave = leave_map.get(key)

            out.append(
                {
                    "date": cal.date,
                    "calendar": CalendarMiniSerializer(cal).data,
                    "biometric": (
                        BiometricTaskDataSerializer(biometric).data
                        if biometric
                        else None
                    ),
                    "leave": (LeaveDaySerializer(leave).data if leave else None),
                }
            )
        return out
