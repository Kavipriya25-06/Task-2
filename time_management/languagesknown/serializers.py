from rest_framework import serializers
from ..models import LanguagesKnown


class LanguagesKnownSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguagesKnown
        fields = "__all__"
