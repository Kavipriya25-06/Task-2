from ..models import WorkExperience

from time_management.workexperience.serializers import WorkExperienceSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def work_experience_api(request, id=None):
    if request.method == "GET":

        if id:
            try:
                obj = WorkExperience.objects.get(id=id)
                serializer = WorkExperienceSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except WorkExperience.DoesNotExist:
                return Response(
                    {"error": "WorkExperience date not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = WorkExperience.objects.all()
            serializer = WorkExperienceSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = WorkExperienceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "WorkExperience data added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not id:
            return Response(
                {"error": "WorkExperience ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = WorkExperience.objects.get(id=id)
        except WorkExperience.DoesNotExist:
            return Response(
                {"error": "WorkExperience data not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = WorkExperienceSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "WorkExperience date updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not id:
            return Response(
                {"error": "WorkExperience ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = WorkExperience.objects.get(id=id)
            obj.delete()
            return Response(
                {"message": "WorkExperience date deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except WorkExperience.DoesNotExist:
            return Response(
                {"error": "WorkExperience date not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
