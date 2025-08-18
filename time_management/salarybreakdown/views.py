from ..models import SalaryBreakdown

from time_management.salarybreakdown.serializers import SalaryBreakdownSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def salary_breakdown_api(request, id=None):
    if request.method == "GET":

        if id:
            try:
                obj = SalaryBreakdown.objects.get(id=id)
                serializer = SalaryBreakdownSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except SalaryBreakdown.DoesNotExist:
                return Response(
                    {"error": "SalaryBreakdown data not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = SalaryBreakdown.objects.all()
            serializer = SalaryBreakdownSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = SalaryBreakdownSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "SalaryBreakdown data added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not id:
            return Response(
                {"error": "SalaryBreakdown ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = SalaryBreakdown.objects.get(id=id)
        except SalaryBreakdown.DoesNotExist:
            return Response(
                {"error": "SalaryBreakdown data not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SalaryBreakdownSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "SalaryBreakdown data updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not id:
            return Response(
                {"error": "SalaryBreakdown ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = SalaryBreakdown.objects.get(id=id)
            obj.delete()
            return Response(
                {"message": "SalaryBreakdown data deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except SalaryBreakdown.DoesNotExist:
            return Response(
                {"error": "SalaryBreakdown data not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
