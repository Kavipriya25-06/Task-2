from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from ..models import (
    Project,
    ProjectAssign,
    AreaOfWork,
    Building,
    BuildingAssign,
    Employee,
)
from time_management.project.serializers import (
    ProjectSerializer,
    ProjectAssignSerializer,
    ProjectAndAssignSerializer,
    AreaOfWorkSerializer,
    ProjectFullSerializer,
)
from time_management.building.serializers import (
    BuildingAssignSerializer,
    BuildingAndProjectSerializer,
)


@api_view(["GET", "POST"])
def project_list_create(request):
    if request.method == "GET":
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Project created", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def project_detail(request, project_id):
    try:
        project = Project.objects.get(project_id=project_id)
    except Project.DoesNotExist:
        return Response(
            {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        partial = request.method == "PATCH"
        serializer = ProjectSerializer(project, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Project updated", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        project.delete()
        return Response(
            {"message": "Project deleted"}, status=status.HTTP_204_NO_CONTENT
        )


@api_view(["GET", "POST"])
def project_assign_list_create(request):
    if request.method == "GET":
        projects = ProjectAssign.objects.all()
        serializer = ProjectAssignSerializer(projects, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = ProjectAssignSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Project assigned",
                    "data": serializer.data,
                    "project_assign_id": serializer.data.get("project_assign_id"),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def project_assign_detail(request, project_assign_id):
    try:
        project = ProjectAssign.objects.get(project_assign_id=project_assign_id)
    except ProjectAssign.DoesNotExist:
        return Response(
            {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = ProjectAssignSerializer(project)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        partial = request.method == "PATCH"
        serializer = ProjectAssignSerializer(
            project, data=request.data, partial=partial
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Project assignment updated", "data": serializer.data}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        project.delete()
        return Response(
            {"message": "Project deleted"}, status=status.HTTP_204_NO_CONTENT
        )


@api_view(["GET"])
def project_and_assign(request, project_assign_id=None):
    if project_assign_id:
        try:
            projects = ProjectAssign.objects.get(project_assign_id=project_assign_id)
        except ProjectAssign.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )
        # projects = ProjectAssign.objects.get(project_assign_id=project_assign_id)
        serializer = ProjectAndAssignSerializer(projects)
        return Response(serializer.data)
    else:
        projects = ProjectAssign.objects.all()
        serializer = ProjectAndAssignSerializer(projects, many=True)
        return Response(serializer.data)


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def areaofwork_api(request, id=None):
    if request.method == "GET":
        if id:
            try:
                obj = AreaOfWork.objects.get(id=id)
                serializer = AreaOfWorkSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except AreaOfWork.DoesNotExist:
                return Response(
                    {"error": "AreaOfWork record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = AreaOfWork.objects.all()
            serializer = AreaOfWorkSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = AreaOfWorkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "AreaOfWork created", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not id:
            return Response(
                {"error": "AreaOfWork ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = AreaOfWork.objects.get(id=id)
        except AreaOfWork.DoesNotExist:
            return Response(
                {"error": "AreaOfWork record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AreaOfWorkSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "AreaOfWork updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not id:
            return Response(
                {"error": "AreaOfWork ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = AreaOfWork.objects.get(id=id)
            obj.delete()
            return Response(
                {"message": "AreaOfWork deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except AreaOfWork.DoesNotExist:
            return Response(
                {"error": "AreaOfWork record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["POST"])
@transaction.atomic
def create_full_project_flow(request):
    try:
        # 1. Create Project
        project_data = request.data.get("project")
        project_serializer = ProjectSerializer(data=project_data)
        if project_serializer.is_valid():
            project_instance = project_serializer.save()
        else:
            return Response(
                {
                    "error": "Project creation failed",
                    "details": project_serializer.errors,
                },
                status=400,
            )

        # 2. Assign Project (ProjectAssign)
        assign_data = request.data.get("assign")
        assign_serializer = ProjectAssignSerializer(
            data={
                "project_hours": project_data.get("estimated_hours"),
                "status": assign_data.get("status", "pending"),
                "employee": assign_data.get("employee"),
                "project": project_instance.project_id,
            }
        )

        if assign_serializer.is_valid():
            assign_instance = assign_serializer.save()
        else:
            return Response(
                {
                    "error": "Project assignment failed",
                    "details": assign_serializer.errors,
                },
                status=400,
            )

        # 3. Assign Buildings (BuildingAssign)
        buildings_data = request.data.get("buildings", [])
        building_assignments = []
        for b in buildings_data:
            building_instance = Building.objects.get(building_id=b["building_id"])
            building_assign = BuildingAssign.objects.create(
                building_hours=b["building_hours"],
                status=b.get("status", "pending"),
                building=building_instance,
                project_assign=assign_instance,
            )
            building_assignments.append(building_assign)

        return Response(
            {
                "message": "Project, assignment, and buildings created successfully.",
                "project_id": project_instance.project_id,
                "project_assign_id": assign_instance.project_assign_id,
                "assigned_buildings": [
                    ba.building_assign_id for ba in building_assignments
                ],
            },
            status=201,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def project_screen(request, project_id=None):
    if project_id:
        try:
            projects = ProjectAssign.objects.get(project=project_id)
            assignedProjects = projects.project_assign_id
            # print(assignedProjects)
            try:
                buildings = BuildingAssign.objects.filter(
                    project_assign=assignedProjects
                )
            except BuildingAssign.DoesNotExist:
                return Response(
                    {"error": "building not found"}, status=status.HTTP_404_NOT_FOUND
                )
        except ProjectAssign.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # serializer = ProjectAndAssignSerializer(projects)
        serializer = BuildingAndProjectSerializer(buildings, many=True)
        return Response(serializer.data)
    else:
        projects = ProjectAssign.objects.all()
        serializer = ProjectAndAssignSerializer(projects, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def full_project_view(request, project_id=None):
    if project_id:
        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

    else:
        return Response(
            {"error": "Project id not given"}, status=status.HTTP_404_NOT_FOUND
        )
    serializer = ProjectFullSerializer(project)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def project_creator(request, employee_id=None):
    if employee_id:
        try:
            project = Project.objects.filter(created_by=employee_id)
        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )
    else:
        project = Project.objects.all()

    serializer = ProjectSerializer(project, many=True)
    return Response(serializer.data)
