from rest_framework import serializers
from ..models import LeavesAvailable, CompOff, LeavesTaken


class LeavesAvailableSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavesAvailable
        fields = "__all__"


class LeavesAvailableWithLOPSerializer(serializers.ModelSerializer):
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


class CompOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompOff
        fields = "__all__"
