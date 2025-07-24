from ..models import Education
from time_management.education.serializers import EducationSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def education_api(request, id=None):
    if request.method == "GET":

        if id:
            try:
                obj = Education.objects.get(id=id)
                serializer = EducationSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Education.DoesNotExist:
                return Response(
                    {"error": "Education date not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = Education.objects.all()
            serializer = EducationSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = EducationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Education data added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not id:
            return Response(
                {"error": "Education ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Education.objects.get(id=id)
        except Education.DoesNotExist:
            return Response(
                {"error": "Education data not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EducationSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Education date updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not id:
            return Response(
                {"error": "Education ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Education.objects.get(id=id)
            obj.delete()
            return Response(
                {"message": "Education date deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Education.DoesNotExist:
            return Response(
                {"error": "Education date not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
