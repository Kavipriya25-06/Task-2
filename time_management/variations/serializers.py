from rest_framework import serializers
from ..models import Variation, Project


class VariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = "__all__"
