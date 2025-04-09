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


class TaskAndAssignSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)

    class Meta:
        model = TaskAssign
        fields = [
            "task_assign_id",
            "task",
            "task_hours",
            "status",
            "start_date",
            "end_date",
            "employee",
            "building_assign",
        ]


class TaskAndAssignSerializerTest(serializers.ModelSerializer):
    task_assign = TaskAssignSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "task_assign",
            # "task_id",
            "task_title",
            "task_description",
        ]
