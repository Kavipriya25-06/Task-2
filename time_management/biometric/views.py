from rest_framework.viewsets import ModelViewSet
from ..models import BiometricData, Employee
from time_management.biometric.serializers import BiometricDataSerializer
from time_management.hierarchy.serializers import emp_under_manager
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from datetime import datetime, timedelta
from django.http import JsonResponse


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def biometric_data_api(request, biometric_id=None, employee_id=None):
    if request.method == "GET":
        if biometric_id:
            try:
                obj = BiometricData.objects.get(biometric_id=biometric_id)
                serializer = BiometricDataSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except BiometricData.DoesNotExist:
                return Response(
                    {"error": "Biometric record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        elif employee_id:
            try:
                obj = BiometricData.objects.filter(employee_id=employee_id)
                serializer = BiometricDataSerializer(obj, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except BiometricData.DoesNotExist:
                return Response(
                    {"error": "Biometric record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = BiometricData.objects.all()
            serializer = BiometricDataSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = BiometricDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Biometric record added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not biometric_id:
            return Response(
                {"error": "Biometric ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = BiometricData.objects.get(biometric_id=biometric_id)
        except BiometricData.DoesNotExist:
            return Response(
                {"error": "Biometric record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = BiometricDataSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Biometric record updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not biometric_id:
            return Response(
                {"error": "Biometric ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = BiometricData.objects.get(biometric_id=biometric_id)
            obj.delete()
            return Response(
                {"message": "Biometric record deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except BiometricData.DoesNotExist:
            return Response(
                {"error": "Biometric record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["GET"])
def attendance(request, employee_id=None):
    if employee_id:
        try:
            manager = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        employees = emp_under_manager(manager)

        biometric_qs = BiometricData.objects.filter(employee__in=employees)

        serializer = BiometricDataSerializer(biometric_qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        objs = BiometricData.objects.all()
        serializer = BiometricDataSerializer(objs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def weekly_attendance(request, employee_id=None):

    todaystr = request.query_params.get("today")  # <-- Get the date from filter params
    if todaystr:
        today = datetime.strptime(todaystr, "%Y-%m-%d").date()
    else:
        today = False

    if employee_id:
        try:
            manager = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        employees = emp_under_manager(manager)

        biometric_qs = BiometricData.objects.filter(employee__in=employees)
        if today:
            weekday = today.weekday()
            start = today - timedelta(days=weekday)
            end = start + timedelta(days=6)
            calendar_entries = biometric_qs.filter(date__range=(start, end)).order_by(
                "date"
            )

            serializer = BiometricDataSerializer(calendar_entries, many=True)
        else:
            serializer = BiometricDataSerializer(biometric_qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        objs = BiometricData.objects.all()
        if today:
            weekday = today.weekday()
            start = today - timedelta(days=weekday)
            end = start + timedelta(days=6)
            calendar_entries = objs.filter(date__range=(start, end)).order_by("date")

            serializer = BiometricDataSerializer(calendar_entries, many=True)
        else:
            serializer = BiometricDataSerializer(objs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def weekly_attendance_leave(request, employee_id=None):

    todaystr = request.query_params.get("today")  # <-- Get the date from filter params
    if todaystr:
        today = datetime.strptime(todaystr, "%Y-%m-%d").date()
    else:
        today = False

    if employee_id:
        try:
            manager = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        employees = emp_under_manager(manager)

        biometric_qs = BiometricData.objects.filter(employee__in=employees)
        if today:
            weekday = today.weekday()
            start = today - timedelta(days=weekday)
            end = start + timedelta(days=6)
            calendar_entries = biometric_qs.filter(date__range=(start, end)).order_by(
                "date"
            )

            serializer = BiometricDataSerializer(calendar_entries, many=True)
        else:
            serializer = BiometricDataSerializer(biometric_qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        objs = BiometricData.objects.all()
        if today:
            weekday = today.weekday()
            start = today - timedelta(days=weekday)
            end = start + timedelta(days=6)
            calendar_entries = objs.filter(date__range=(start, end)).order_by("date")

            serializer = BiometricDataSerializer(calendar_entries, many=True)
        else:
            serializer = BiometricDataSerializer(objs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def attendance_admin(request, employee_id=None):
    if employee_id:
        try:
            manager = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        employees = emp_under_manager(manager)

        biometric_qs = BiometricData.objects.filter(employee__in=employees)
        modified_biometric = biometric_qs.filter(modified_by=employee_id)

        serializer = BiometricDataSerializer(modified_biometric, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        objs = BiometricData.objects.all()
        serializer = BiometricDataSerializer(objs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

