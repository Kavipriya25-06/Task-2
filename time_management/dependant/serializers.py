from rest_framework import serializers
from ..models import Dependant


class DependantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dependant
        fields = "__all__"
