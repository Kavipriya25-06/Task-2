from rest_framework import serializers
from ..models import Task, TaskAssign


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class TaskAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAssign
        fields = "__all__"
