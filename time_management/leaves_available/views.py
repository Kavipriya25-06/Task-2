from rest_framework.viewsets import ModelViewSet
from ..models import LeavesAvailable, CompOff

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from time_management.leaves_available.serializers import (
    LeavesAvailableSerializer,
    CompOffSerializer,
)


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
        if not leave_avail_id and not employee_id:
            return Response(
                {"error": "Leave record ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            if leave_avail_id:
                obj = LeavesAvailable.objects.get(leave_avail_id=leave_avail_id)
            elif employee_id:
                obj = LeavesAvailable.objects.get(employee_id=employee_id)
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


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def comp_off_api(request, id=None):
    if request.method == "GET":
        if id:
            try:
                obj = CompOff.objects.get(id=id)
                serializer = CompOffSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except CompOff.DoesNotExist:
                return Response(
                    {"error": "Leave record with leave id not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        else:
            objs = CompOff.objects.all()
            serializer = CompOffSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = CompOffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Leave balance created", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not id:
            return Response(
                {"error": "Leave record ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = CompOff.objects.get(id=id)
        except CompOff.DoesNotExist:
            return Response(
                {"error": "Leave record not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = CompOffSerializer(
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
        if not id:
            return Response(
                {"error": "Leave record ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = CompOff.objects.get(id=id)
            obj.delete()
            return Response(
                {"message": "Leave balance deleted"}, status=status.HTTP_204_NO_CONTENT
            )
        except CompOff.DoesNotExist:
            return Response(
                {"error": "Leave record not found"}, status=status.HTTP_404_NOT_FOUND
            )


def get_comp_off(hours_worked):
    """
    Returns:
    - 0.5 → Half day
    - 1.0 → Full day
    - 0.0 → No deduction (if above max for both)
    """

    # First, check for half day
    try:
        half_day = CompOff.objects.get(leave_type="half_day")
        if half_day.min_hours <= hours_worked <= half_day.max_hours:
            return 0.5
    except CompOff.DoesNotExist:
        pass  # No threshold defined

    # Then, check for full day
    try:
        full_day = CompOff.objects.get(leave_type="full_day")
        if full_day.min_hours <= hours_worked <= full_day.max_hours:
            return 1.0
    except CompOff.DoesNotExist:
        pass

    # If none matched → no deduction
    return 0.0
