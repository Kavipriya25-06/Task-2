from rest_framework import serializers
from ..models import Building, BuildingAssign

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = '__all__'


class BuildingAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingAssign
        fields = "__all__"
