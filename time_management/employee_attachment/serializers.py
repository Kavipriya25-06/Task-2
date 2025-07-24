from rest_framework import serializers
from ..models import EmployeeAttachment


class EmployeeAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAttachment
        fields = "__all__"
