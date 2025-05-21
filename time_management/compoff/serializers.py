from rest_framework import serializers
from ..models import Calendar, CompOffRequest


class CompOffRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompOffRequest
        fields = "__all__"
