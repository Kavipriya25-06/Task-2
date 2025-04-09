from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..models import Project, ProjectAssign
from time_management.project.serializers import (
    ProjectSerializer,
    ProjectAssignSerializer,
    ProjectAndAssignSerializer,
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
                {"message": "Project assigned", "data": serializer.data},
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
