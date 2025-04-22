from rest_framework.viewsets import ModelViewSet
from ..models import BiometricData, Employee, TimeSheet
from time_management.biometric.serializers import BiometricDataSerializer
from time_management.time_sheet.serializers import TimeSheetDataSerializer
from time_management.hierarchy.serializers import emp_under_manager
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from datetime import datetime, timedelta
from django.http import JsonResponse


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def timesheet_data_api(request, timesheet_id=None):
    if request.method == "GET":
        if timesheet_id:
            try:
                obj = TimeSheet.objects.get(timesheet_id=timesheet_id)
                serializer = TimeSheetDataSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except TimeSheet.DoesNotExist:
                return Response(
                    {"error": "TimeSheetData record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = TimeSheet.objects.all()
            serializer = TimeSheetDataSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = TimeSheetDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "TimeSheetData record added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not timesheet_id:
            return Response(
                {"error": "TimeSheetData ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = TimeSheet.objects.get(timesheet_id=timesheet_id)
        except TimeSheet.DoesNotExist:
            return Response(
                {"error": "TimeSheetData record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TimeSheetDataSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "TimeSheetData record updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not timesheet_id:
            return Response(
                {"error": "TimeSheetData ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = TimeSheet.objects.get(timesheet_id=timesheet_id)
            obj.delete()
            return Response(
                {"message": "TimeSheetData record deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except TimeSheet.DoesNotExist:
            return Response(
                {"error": "TimeSheetData record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
