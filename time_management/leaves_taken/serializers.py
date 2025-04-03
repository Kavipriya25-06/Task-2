from rest_framework import serializers
from ..models import LeavesTaken


class LeavesTakenSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavesTaken
        fields = "__all__"
