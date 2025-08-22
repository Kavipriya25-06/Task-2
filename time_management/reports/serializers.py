from rest_framework import serializers
from django.db.models import Sum, Q
from datetime import timedelta, date
from django.db.models.functions import TruncWeek, TruncMonth, TruncYear
from ..models import (
    Project,
    ProjectAssign,
    Building,
    BuildingAssign,
    Task,
    TaskAssign,
    Variation,
    TimeSheet,
    Employee,
    LeavesAvailable,
    LeavesTaken,
    Calendar,
)
from collections import defaultdict
from datetime import timedelta
import calendar

from time_management.project.serializers import (
    VariationSerializer,
)

from time_management.task.serializers import TaskEntrySerializer


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "employee_name",
            "employee_code",
            "doj",
            "status",
            "resignation_date",
            "department",
        ]


class ProjectAndAssignSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectAssign
        fields = [
            "project_assign_id",
            "status",
        ]


# Task Serializer
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["task_id", "task_code", "task_title", "status"]


# Task Assign Serializer
class TaskAssignSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)

    task_consumed_hours = serializers.SerializerMethodField()

    class Meta:
        model = TaskAssign
        fields = [
            "task_assign_id",
            "status",
            "start_date",
            "task",
            "task_consumed_hours",
        ]

    def get_task_consumed_hours(self, obj):
        total = (
            TimeSheet.objects.filter(task_assign=obj, approved=True).aggregate(
                total=Sum("task_hours")
            )["total"]
            or 0
        )
        return float(total)


# Building Serializer
class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ["building_id", "building_code", "building_title"]


# Building Assign Serializer
class BuildingAssignFullSerializer(serializers.ModelSerializer):
    building = BuildingSerializer(read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = BuildingAssign
        fields = [
            "building_assign_id",
            "status",
            "building",
            "tasks",
        ]

    def get_tasks(self, obj):
        task_assigns = TaskAssign.objects.filter(building_assign=obj)
        return TaskAssignSerializer(task_assigns, many=True).data


# Project Assign Serializer
class ProjectAssignFullSerializer(serializers.ModelSerializer):

    buildings = serializers.SerializerMethodField()

    class Meta:
        model = ProjectAssign
        fields = [
            "project_assign_id",
            "status",
            "buildings",
        ]

    def get_buildings(self, obj):
        building_assigns = BuildingAssign.objects.filter(project_assign=obj)
        return BuildingAssignFullSerializer(building_assigns, many=True).data


# Full Project Serializer
class ProjectHoursSerializer(serializers.ModelSerializer):

    assigns = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "project_id",
            "project_code",
            "project_title",
            "discipline_code",
            "start_date",
            "total_hours",
            "consumed_hours",
            "assigns",
        ]

    def get_assigns(self, obj):
        assigns = ProjectAssign.objects.filter(project=obj)
        return ProjectAssignFullSerializer(assigns, many=True).data

    def get_variation(self, obj):
        variation = Variation.objects.filter(project=obj)
        return VariationSerializer(variation, many=True).data


# weekly Project Serializer
class ProjectWeeklyHoursSerializer(serializers.ModelSerializer):

    task_consumed_hours_by_week = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "project_id",
            "project_code",
            "project_title",
            "discipline_code",
            "start_date",
            "total_hours",
            "consumed_hours",
            "task_consumed_hours_by_week",
        ]

    def get_task_consumed_hours_by_week(self, obj):
        # Group timesheet entries by week and sum approved hours
        qs = (
            TimeSheet.objects.filter(
                task_assign__building_assign__project_assign__project=obj, approved=True
            )
            .annotate(week=TruncWeek("date"))
            .values("week")
            .annotate(total=Sum("task_hours"))
            .order_by("week")
        )
        return [
            {
                "week": (
                    entry["week"].strftime("%G-W%V") if entry["week"] else "Unknown"
                ),
                "hours": float(entry["total"]),
            }
            for entry in qs
        ]


class ProjectDepartmentWeeklyStatsSerializer(serializers.ModelSerializer):
    weekly_stats = serializers.SerializerMethodField()

    class Meta:
        model = Calendar
        fields = [
            "calendar_id",
            "date",
            "weekly_stats",  # Combines hours, working days, active employees
        ]

    def get_weekly_stats(self, obj):
        filter_department = self.context.get("department")
        filter_year = self.context.get("year")

        # Step 1: Get all weeks in the year
        calendar_weeks = (
            Calendar.objects.filter(year=filter_year)
            .annotate(week=TruncWeek("date"))
            .values("week")
            .order_by("week")
            .distinct()
        )

        stats = []
        for entry in calendar_weeks:
            week_start = entry["week"]
            if not week_start:
                stats.append(
                    {
                        "week": "Unknown",
                        "working_days": 0,
                        "active_employees": 0,
                    }
                )
                continue

            week_end = week_start + timedelta(days=6)

            # Step 2: Working Days
            working_days = Calendar.objects.filter(
                date__range=(week_start, week_end), is_weekend=False
            ).count()

            # Identify active employees on the week
            active_employees = Employee.objects.filter(
                Q(doj__lte=week_start),
                Q(relieving_date__isnull=True) | Q(relieving_date__gte=week_start),
                status="active",
            )

            if filter_department:
                active_employees = active_employees.filter(department=filter_department)

            active_employee_count = active_employees.count()

            stats.append(
                {
                    "week": week_start.strftime("%G-W%V"),
                    "working_days": working_days,
                    # "hours": float(total_hours),
                    "active_employees": active_employee_count,
                }
            )

        return stats


# weekly Project Serializer
class ProjectDepartmentWeeklyHoursSerializer(serializers.ModelSerializer):

    task_consumed_hours_by_week = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "project_id",
            "project_code",
            "project_title",
            "discipline_code",
            "start_date",
            "total_hours",
            "consumed_hours",
            "task_consumed_hours_by_week",
        ]

    # def get_working_days(self, obj):
    #     filter_department = self.context.get("department")
    #     filter_year = self.context.get("year")

    #     if filter_year:
    #         qs = (
    #             Calendar.objects.filter(year=filter_year)
    #             .annotate(week=TruncWeek("date"))
    #             .values("week")
    #             .order_by("week")
    #             .distinct()
    #         )
    #     else:
    #         qs = (
    #             Calendar.objects.filter(year=filter_year)
    #             .annotate(week=TruncWeek("date"))
    #             .values("week")
    #             .order_by("week")
    #             .distinct()
    #         )

    #     # Calculate working days per week
    #     result = []
    #     for entry in qs:
    #         week_start = entry["week"]
    #         if not week_start:
    #             result.append({"week": "Unknown", "working_days": 0})
    #             continue

    #         week_end = week_start + timedelta(days=6)
    #         working_days = Calendar.objects.filter(
    #             date__range=(week_start, week_end),
    #             is_weekend=False,
    #             # is_holiday=False,
    #         ).count()

    #         result.append(
    #             {"week": week_start.strftime("%Y-W%U"), "working_days": working_days}
    #         )

    #     return result

    # def get_working_days(self, obj):

    #     # Group timesheet entries by week and sum approved hours
    #     request = self.context.get("request")
    #     filter_department = self.context.get("department")
    #     # print("Department", filter_department)
    #     if filter_department:
    #         qs = (
    #             TimeSheet.objects.filter(
    #                 task_assign__building_assign__project_assign__project=obj,
    #                 approved=True,
    #                 employee__department=filter_department,
    #             )
    #             .annotate(week=TruncWeek("date"))
    #             .values("week")
    #             .annotate(total=Sum("task_hours"))
    #             .order_by("week")
    #         )
    #     else:
    #         qs = (
    #             TimeSheet.objects.filter(
    #                 task_assign__building_assign__project_assign__project=obj,
    #                 approved=True,
    #             )
    #             .annotate(week=TruncWeek("date"))
    #             .values("week")
    #             .annotate(total=Sum("task_hours"))
    #             .order_by("week")
    #         )

    #     # Step 2: For each week, calculate working days
    #     result = []
    #     for entry in qs:
    #         week_start = entry["week"]
    #         if not week_start:
    #             result.append(
    #                 {
    #                     "week": "Unknown",
    #                     "hours": float(entry["total"]),
    #                     "working_days": 0,
    #                 }
    #             )
    #             continue

    #         week_end = week_start + timedelta(days=6)
    #         working_days = Calendar.objects.filter(
    #             date__range=(week_start, week_end),
    #             is_weekend=False,
    #             is_holiday=False,
    #         ).count()

    #         result.append(
    #             {
    #                 "week": week_start.strftime("%Y-W%U"),
    #                 "hours": float(entry["total"]),
    #                 "working_days": working_days,
    #             }
    #         )

    #     return result

    def get_task_consumed_hours_by_week(self, obj):
        # Group timesheet entries by week and sum approved hours
        request = self.context.get("request")
        filter_department = self.context.get("department")
        # print("Department", filter_department)
        if filter_department:
            qs = (
                TimeSheet.objects.filter(
                    task_assign__building_assign__project_assign__project=obj,
                    approved=True,
                    employee__department=filter_department,
                )
                .annotate(week=TruncWeek("date"))
                .values("week")
                .annotate(total=Sum("task_hours"))
                .order_by("week")
            )
        else:
            qs = (
                TimeSheet.objects.filter(
                    task_assign__building_assign__project_assign__project=obj,
                    approved=True,
                )
                .annotate(week=TruncWeek("date"))
                .values("week")
                .annotate(total=Sum("task_hours"))
                .order_by("week")
            )
        return [
            {
                "week": (
                    entry["week"].strftime("%G-W%V") if entry["week"] else "Unknown"
                ),
                "hours": float(entry["total"]),
            }
            for entry in qs
        ]


# Yearly Project Serializer
class ProjectYearlyHoursSerializer(serializers.ModelSerializer):

    task_consumed_hours_by_year = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "project_id",
            "project_code",
            "project_title",
            "discipline_code",
            "start_date",
            "total_hours",
            "consumed_hours",
            "task_consumed_hours_by_year",
        ]

    def get_task_consumed_hours_by_year(self, obj):
        # Group timesheet entries by week and sum approved hours
        qs = (
            TimeSheet.objects.filter(
                task_assign__building_assign__project_assign__project=obj, approved=True
            )
            .annotate(year=TruncYear("date"))
            .values("year")
            .annotate(total=Sum("task_hours"))
            .order_by("year")
        )
        return [
            {
                "year": (entry["year"].strftime("%Y") if entry["year"] else "Unknown"),
                "hours": float(entry["total"]),
            }
            for entry in qs
        ]


# Monthly Project Serializer
class ProjectMonthlyHoursSerializer(serializers.ModelSerializer):

    task_consumed_hours_by_month = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "project_id",
            "project_code",
            "project_title",
            "discipline_code",
            "start_date",
            "total_hours",
            "consumed_hours",
            "task_consumed_hours_by_month",
        ]

    def get_task_consumed_hours_by_month(self, obj):
        # Group timesheet entries by week and sum approved hours
        qs = (
            TimeSheet.objects.filter(
                task_assign__building_assign__project_assign__project=obj, approved=True
            )
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total=Sum("task_hours"))
            .order_by("month")
        )
        return [
            {
                "month": (
                    entry["month"].strftime("%Y-%m") if entry["month"] else "Unknown"
                ),
                "hours": float(entry["total"]),
            }
            for entry in qs
        ]


class TimeSheetTaskSerializer(serializers.ModelSerializer):
    task_assign = TaskEntrySerializer(read_only=True)
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = TimeSheet
        fields = "__all__"


class LeavesAvailableSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = LeavesAvailable
        fields = "__all__"


class LeavesFullAvailableSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    lop = serializers.SerializerMethodField()

    class Meta:
        model = LeavesAvailable
        fields = [
            "leave_avail_id",
            "sick_leave",
            "casual_leave",
            "comp_off",
            "earned_leave",
            "employee",
            "lop",
        ]

    def get_lop(self, obj):
        request = self.context.get("request")
        filter_year = request.GET.get("year") if request else None

        leaves = LeavesTaken.objects.filter(
            employee=obj.employee, leave_type="lop", start_date__year=filter_year
        )

        total_lop = 0

        for leave in leaves:

            total_lop += float(leave.duration)

        return total_lop


def add_months(month, year, offset):
    new_month = month + offset
    new_year = year + (new_month - 1) // 12
    new_month = ((new_month - 1) % 12) + 1
    return new_month, new_year


class EmployeeLOPSerializer(serializers.ModelSerializer):

    lop_by_month = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "employee_name",
            "employee_code",
            "doj",
            "status",
            "resignation_date",
            "department",
            "lop_by_month",
        ]

    def get_lop_by_month(self, obj):

        request = self.context.get("request")
        filter_year = request.GET.get("year") if request else None

        leaves = LeavesTaken.objects.filter(employee=obj, leave_type="lop")
        month_buckets = defaultdict(float)

        for leave in leaves:
            current_date = leave.start_date
            end_date = leave.end_date or leave.start_date
            total_days = (end_date - current_date).days + 1
            duration_per_day = float(leave.duration) / total_days

            while current_date <= end_date:
                day = current_date.day
                month = current_date.month
                year = current_date.year

                # if day >= 21:
                #     payroll_month, payroll_year = add_months(month, year, 2)
                # else:
                #     payroll_month, payroll_year = add_months(month, year, 1)

                payroll_month = month
                payroll_year = year

                key = f"{payroll_year}-{str(payroll_month).zfill(2)}"

                # Apply year filter
                if filter_year and str(payroll_year) != str(filter_year):
                    current_date += timedelta(days=1)
                    continue

                month_buckets[key] += duration_per_day

                current_date += timedelta(days=1)

        return [
            {"month": month, "days": round(days, 2)}
            for month, days in sorted(month_buckets.items())
        ]


# Calendar Serializer
class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = "__all__"
