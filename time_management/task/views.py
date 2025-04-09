from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..models import Project, ProjectAssign
from time_management.project.serializers import (
    ProjectSerializer,
    ProjectAssignSerializer,
)

from ..models import Task, TaskAssign
from time_management.task.serializers import (
    TaskSerializer,
    TaskAssignSerializer,
    TaskAndAssignSerializer,
    TaskAndAssignSerializerTest,
)


@api_view(["GET", "POST"])
def task_list_create(request):
    if request.method == "GET":
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Task created", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def task_detail(request, task_id):
    try:
        task = Task.objects.get(task_id=task_id)
    except Task.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        partial = request.method == "PATCH"
        serializer = TaskSerializer(task, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Task updated", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        task.delete()
        return Response({"message": "Task deleted"}, status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
def task_assign_list_create(request):
    if request.method == "GET":
        tasks = TaskAssign.objects.all()
        serializer = TaskAssignSerializer(tasks, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = TaskAssignSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Task assigned", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def task_assign_detail(request, task_assign_id):
    try:
        task = TaskAssign.objects.get(task_assign_id=task_assign_id)
    except TaskAssign.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = TaskAssignSerializer(task)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        partial = request.method == "PATCH"
        serializer = TaskAssignSerializer(task, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Task assignment updated", "data": serializer.data}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        task.delete()
        return Response({"message": "Task deleted"}, status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def task_and_assign(request, task_assign_id=None):
    if task_assign_id:
        try:
            tasks = TaskAssign.objects.get(task_assign_id=task_assign_id)
        except TaskAssign.DoesNotExist:
            return Response(
                {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
            )
        # projects = ProjectAssign.objects.get(project_assign_id=project_assign_id)
        serializer = TaskAndAssignSerializer(tasks)
        return Response(serializer.data)
    else:
        tasks = TaskAssign.objects.all()
        serializer = TaskAndAssignSerializer(tasks, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def task_and_assign_test(request, task_id=None):
    if task_id:
        try:
            tasks = Task.objects.get(task_id=task_id)
        except Task.DoesNotExist:
            return Response(
                {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
            )
        # projects = ProjectAssign.objects.get(project_assign_id=project_assign_id)
        serializer = TaskAndAssignSerializerTest(tasks)
        return Response(serializer.data)
    else:
        tasks = Task.objects.all()
        serializer = TaskAndAssignSerializerTest(tasks, many=True)
        return Response(serializer.data)
