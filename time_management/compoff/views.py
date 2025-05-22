from rest_framework.viewsets import ModelViewSet
from ..models import Calendar, CompOffRequest, CompOff, Employee, TimeSheet
from time_management.calendar.serializers import CalendarSerializer
from time_management.compoff.serializers import (
    CompOffRequestSerializer,
    CompOffRequestEmployeeSerializer,
    CompOffRequestTaskSerializer,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from time_management.hierarchy.serializers import get_emp_under_manager


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def compoff_request_api(request, compoff_request_id=None):
    if request.method == "GET":

        if compoff_request_id:
            try:
                obj = CompOffRequest.objects.get(compoff_request_id=compoff_request_id)
                serializer = CompOffRequestSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except CompOffRequest.DoesNotExist:
                return Response(
                    {"error": "CompOffRequest date not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = CompOffRequest.objects.all()
            serializer = CompOffRequestSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = CompOffRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "CompOffRequest date added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not compoff_request_id:
            return Response(
                {"error": "CompOffRequest ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = CompOffRequest.objects.get(compoff_request_id=compoff_request_id)
        except CompOffRequest.DoesNotExist:
            return Response(
                {"error": "CompOffRequest date not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CompOffRequestSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "CompOffRequest date updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not compoff_request_id:
            return Response(
                {"error": "CompOffRequest ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = CompOffRequest.objects.get(compoff_request_id=compoff_request_id)
            obj.delete()
            return Response(
                {"message": "CompOffRequest date deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except CompOffRequest.DoesNotExist:
            return Response(
                {"error": "CompOffRequest date not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["GET"])
def compoff_view_api(request, compoff_request_id=None, employee_id=None):

    todaystr = request.query_params.get("today")  # <-- Get the date from filter params
    if todaystr:
        today = datetime.strptime(todaystr, "%Y-%m-%d").date()
    else:
        today = False

    if compoff_request_id:
        try:
            compoff = CompOffRequest.objects.get(compoff_request_id=compoff_request_id)

        except CompOffRequest.DoesNotExist:
            return Response(
                {"error": "compoff not found"}, status=status.HTTP_404_NOT_FOUND
            )
    elif employee_id:
        try:
            compoffs = CompOffRequest.objects.filter(employee_id=employee_id)
            if today:
                compoff = compoffs.filter(date=today)
            else:
                compoff = compoffs
        except CompOffRequest.DoesNotExist:
            return Response(
                {"error": "compoff not found"}, status=status.HTTP_404_NOT_FOUND
            )
    else:
        compoff = CompOffRequest.objects.all()

    serializer = CompOffRequestTaskSerializer(compoff, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def compoff_manager_view_api(request, compoff_request_id=None, manager_id=None):

    todaystr = request.query_params.get("today")  # <-- Get the date from filter params
    if todaystr:
        today = datetime.strptime(todaystr, "%Y-%m-%d").date()
    else:
        today = False

    if compoff_request_id:
        try:
            compoff = CompOffRequest.objects.get(compoff_request_id=compoff_request_id)

        except CompOffRequest.DoesNotExist:
            return Response(
                {"error": "compoff not found"}, status=status.HTTP_404_NOT_FOUND
            )
    elif manager_id:
        try:
            employee_qs = get_emp_under_manager(manager_id)

            compoffs = CompOffRequest.objects.filter(employee__in=employee_qs)
            if today:
                compoff = compoffs.filter(date=today)
            else:
                compoff = compoffs
        except CompOffRequest.DoesNotExist:
            return Response(
                {"error": "compoff not found"}, status=status.HTTP_404_NOT_FOUND
            )
    else:
        compoff = CompOffRequest.objects.all()

    serializer = CompOffRequestTaskSerializer(compoff, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
