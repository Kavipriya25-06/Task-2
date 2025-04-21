from rest_framework.viewsets import ModelViewSet
from ..models import Calendar
from time_management.calendar.serializers import CalendarSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def calendar_api(request, calendar_id=None):
    if request.method == "GET":
        year = request.query_params.get("year")  # <-- Get the 'year' from query params
        month = request.query_params.get("month")
        if calendar_id:
            try:
                obj = Calendar.objects.get(calendar_id=calendar_id)
                serializer = CalendarSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Calendar.DoesNotExist:
                return Response(
                    {"error": "Calendar date not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = Calendar.objects.all()
            #  Apply filter if year query param is present
            # year = int(year) if year else datetime.now().year
            if year:
                objs = objs.filter(year=year)
            # objs = Calendar.objects.filter(year=year)
            serializer = CalendarSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = CalendarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Calendar date added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not calendar_id:
            return Response(
                {"error": "Calendar ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Calendar.objects.get(calendar_id=calendar_id)
        except Calendar.DoesNotExist:
            return Response(
                {"error": "Calendar date not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = CalendarSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Calendar date updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not calendar_id:
            return Response(
                {"error": "Calendar ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Calendar.objects.get(calendar_id=calendar_id)
            obj.delete()
            return Response(
                {"message": "Calendar date deleted"}, status=status.HTTP_204_NO_CONTENT
            )
        except Calendar.DoesNotExist:
            return Response(
                {"error": "Calendar date not found"}, status=status.HTTP_404_NOT_FOUND
            )
