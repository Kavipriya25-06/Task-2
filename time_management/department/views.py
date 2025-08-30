from ..models import Department

from time_management.department.serializers import DepartmentSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def department_api(request, id=None):
    if request.method == "GET":

        if id:
            try:
                obj = Department.objects.get(id=id)
                serializer = DepartmentSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Department.DoesNotExist:
                return Response(
                    {"error": "Department date not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = Department.objects.all()
            serializer = DepartmentSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Department data added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not id:
            return Response(
                {"error": "Department ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Department.objects.get(id=id)
        except Department.DoesNotExist:
            return Response(
                {"error": "Department data not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DepartmentSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Department date updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not id:
            return Response(
                {"error": "Department ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Department.objects.get(id=id)
            obj.delete()
            return Response(
                {"message": "Department date deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Department.DoesNotExist:
            return Response(
                {"error": "Department date not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
