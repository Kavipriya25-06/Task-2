from ..models import Modifications
from time_management.modifications.serializers import ModificationsSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def modifications_api(request, id=None):
    if request.method == "GET":

        if id:
            try:
                obj = Modifications.objects.get(id=id)
                serializer = ModificationsSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Modifications.DoesNotExist:
                return Response(
                    {"error": "Modifications date not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = Modifications.objects.all()
            serializer = ModificationsSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = ModificationsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Modifications data added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not id:
            return Response(
                {"error": "Modifications ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Modifications.objects.get(id=id)
        except Modifications.DoesNotExist:
            return Response(
                {"error": "Modifications data not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ModificationsSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Modifications date updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not id:
            return Response(
                {"error": "Modifications ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Modifications.objects.get(id=id)
            obj.delete()
            return Response(
                {"message": "Modifications date deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Modifications.DoesNotExist:
            return Response(
                {"error": "Modifications date not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
