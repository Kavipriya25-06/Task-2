

from rest_framework import serializers
from ..models import Modifications


class ModificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modifications
        fields = "__all__"
