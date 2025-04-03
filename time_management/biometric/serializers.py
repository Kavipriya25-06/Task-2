from rest_framework import serializers
from ..models import BiometricData


class BiometricDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiometricData
        fields = "__all__"
