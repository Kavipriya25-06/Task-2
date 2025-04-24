from rest_framework.viewsets import ModelViewSet
from ..models import LeavesAvailable

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from time_management.leaves_available.serializers import LeavesAvailableSerializer


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def leaves_available_api(request, leave_avail_id=None, employee_id=None):
    if request.method == "GET":
        if leave_avail_id:
            try:
                obj = LeavesAvailable.objects.get(leave_avail_id=leave_avail_id)
                serializer = LeavesAvailableSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except LeavesAvailable.DoesNotExist:
                return Response(
                    {"error": "Leave record with leave id not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        elif employee_id:
            try:
                obj = LeavesAvailable.objects.get(employee_id=employee_id)
                serializer = LeavesAvailableSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except LeavesAvailable.DoesNotExist:
                return Response(
                    {"error": "Leave record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = LeavesAvailable.objects.all()
            serializer = LeavesAvailableSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = LeavesAvailableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Leave balance created", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not leave_avail_id:
            return Response(
                {"error": "Leave record ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = LeavesAvailable.objects.get(leave_avail_id=leave_avail_id)
        except LeavesAvailable.DoesNotExist:
            return Response(
                {"error": "Leave record not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = LeavesAvailableSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Leave balance updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not leave_avail_id:
            return Response(
                {"error": "Leave record ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = LeavesAvailable.objects.get(leave_avail_id=leave_avail_id)
            obj.delete()
            return Response(
                {"message": "Leave balance deleted"}, status=status.HTTP_204_NO_CONTENT
            )
        except LeavesAvailable.DoesNotExist:
            return Response(
                {"error": "Leave record not found"}, status=status.HTTP_404_NOT_FOUND
            )
