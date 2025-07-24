from ..models import Dependant
from time_management.dependant.serializers import DependantSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def dependant_api(request, id=None):
    if request.method == "GET":

        if id:
            try:
                obj = Dependant.objects.get(id=id)
                serializer = DependantSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Dependant.DoesNotExist:
                return Response(
                    {"error": "Dependant date not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = Dependant.objects.all()
            serializer = DependantSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = DependantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Dependant data added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not id:
            return Response(
                {"error": "Dependant ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Dependant.objects.get(id=id)
        except Dependant.DoesNotExist:
            return Response(
                {"error": "Dependant data not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DependantSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Dependant date updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not id:
            return Response(
                {"error": "Dependant ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Dependant.objects.get(id=id)
            obj.delete()
            return Response(
                {"message": "Dependant date deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Dependant.DoesNotExist:
            return Response(
                {"error": "Dependant date not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
