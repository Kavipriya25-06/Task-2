from ..models import Modifications, Designation

from time_management.designation.serializers import DesignationSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def designation_api(request, id=None):
    if request.method == "GET":

        if id:
            try:
                obj = Designation.objects.get(id=id)
                serializer = DesignationSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Designation.DoesNotExist:
                return Response(
                    {"error": "Designation date not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = Designation.objects.all()
            serializer = DesignationSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = DesignationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Designation data added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not id:
            return Response(
                {"error": "Designation ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Designation.objects.get(id=id)
        except Designation.DoesNotExist:
            return Response(
                {"error": "Designation data not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DesignationSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Designation date updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not id:
            return Response(
                {"error": "Designation ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Designation.objects.get(id=id)
            obj.delete()
            return Response(
                {"message": "Designation date deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Designation.DoesNotExist:
            return Response(
                {"error": "Designation date not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
