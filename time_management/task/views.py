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
    TaskBuildingSerializer,
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


@api_view(["GET"])
def task_building(request, task_assign_id=None):
    if task_assign_id:
        try:
            tasks = TaskAssign.objects.get(task_assign_id=task_assign_id)
        except TaskAssign.DoesNotExist:
            return Response(
                {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = TaskBuildingSerializer(tasks)
        return Response(serializer.data)
    else:
        tasks = TaskAssign.objects.all()
        serializer = TaskBuildingSerializer(tasks, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def task_by_employee(request, employee_id=None):
    default_project_codes = [
        "99000",
        "99001",
        "99005",
        "99007",
        "99008",
        "1",
        "1a",
        "2001000",
    ]
    default_tasks = TaskAssign.objects.filter(
        building_assign__project_assign__project__project_code__in=default_project_codes
    )
    # print("Default project", default_tasks)
    if employee_id:
        try:
            tasks = TaskAssign.objects.filter(employee__employee_id=employee_id)
            all_tasks = default_tasks | tasks
        except TaskAssign.DoesNotExist:
            return Response(
                {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = TaskBuildingSerializer(all_tasks, many=True)
        return Response(serializer.data)
    else:
        tasks = TaskAssign.objects.all()
        serializer = TaskBuildingSerializer(tasks, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def default_task_by_employee(request, employee_id=None):
    default_project_codes = [
        "99000",
        "99001",
        "99005",
        "99007",
        "99008",
        "1",
        "1a",
        "2001000",
    ]
    default_tasks = TaskAssign.objects.filter(
        building_assign__project_assign__project__project_code__in=default_project_codes
    )

    serializer = TaskBuildingSerializer(default_tasks, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def default_tasks(request, employee_id=None):
    default_project_codes = [
        "99000",
        "99001",
        "99005",
        "99007",
        "99008",
        "1",
        "1a",
        "2001000",
    ]
    default_tasks = TaskAssign.objects.filter(
        building_assign__project_assign__project__project_code__in=default_project_codes
    )

    # Extract Task objects
    task_ids = default_tasks.values_list("task__task_id", flat=True)
    # tasks = Task.objects.filter(task_id__in=task_ids).distinct()

    tasks = Task.objects.filter(
        taskassign__building_assign__project_assign__project__project_code__in=default_project_codes
    ).distinct()

    print("Other tasks", tasks)

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def other_tasks(request, employee_id=None):
    default_project_codes = [
        "99000",
        "99001",
        "99002",
        "99003",
        "99004",
        "99004a",
        "99005",
        "99006",
        "99007",
        "99008",
        "99009",
        "1",
        "1a",
        "2001000",
    ]
    # other_tasks_assigned = TaskAssign.objects.exclude(
    #     building_assign__project_assign__project__project_code__in=default_project_codes
    # )

    # for task in other_tasks_assigned:
    #     other_tasks = task.task

    #     print("Other tasks", other_tasks)

    # # Extract Task objects
    # task_ids = other_tasks_assigned.values_list("task__task_id", flat=True)
    # tasks = Task.objects.filter(task_id__in=task_ids).distinct()

    tasks = Task.objects.exclude(
        taskassign__building_assign__project_assign__project__project_code__in=default_project_codes
    ).distinct()

    print("Other tasks", tasks)

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


# views.py
@api_view(["POST"])
def upsert_tasks_assigned(request):
    data = request.data
    task = data.get("task")
    data_hours = float(data.get("task_hours", 0))
    building_assign = data.get("building_assign")
    employee_ids = data.get("employee", [])

    instance = TaskAssign.objects.filter(
        task_id=task, building_assign_id=building_assign
    ).first()

    # Convert single ID to list
    if not isinstance(employee_ids, list):
        employee_ids = [employee_ids]

    if instance:
        data_without_employee = data.copy()
        data_without_employee.pop("employee", None)
        data_without_employee.pop("task_hours", None)
        serializer = TaskAssignSerializer(
            instance, data=data_without_employee, partial=True
        )
    else:
        serializer = TaskAssignSerializer(data=data)

    if serializer.is_valid():
        task_obj = serializer.save()
        existing_ids = set(task_obj.employee.values_list("employee_id", flat=True))
        new_ids = set(employee_ids)
        to_add = list(new_ids - existing_ids)
        print("Existing", existing_ids)
        print("new ids", new_ids)
        print("to add", to_add)
        task_obj.task_hours = float(task_obj.task_hours or 0) + data_hours
        task_obj.save()
        # task_obj.employee.add(*employee_ids)  # set M2M employee field
        if to_add:
            task_obj.employee.add(*to_add)
        return Response(TaskAssignSerializer(task_obj).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
