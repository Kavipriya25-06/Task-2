from ..models import Assets
from time_management.assets.serializers import AssetsSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def assets_api(request, id=None):
    if request.method == "GET":

        if id:
            try:
                obj = Assets.objects.get(id=id)
                serializer = AssetsSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Assets.DoesNotExist:
                return Response(
                    {"error": "Assets date not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = Assets.objects.all()
            serializer = AssetsSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = AssetsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Assets data added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not id:
            return Response(
                {"error": "Assets ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Assets.objects.get(id=id)
        except Assets.DoesNotExist:
            return Response(
                {"error": "Assets data not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AssetsSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Assets date updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not id:
            return Response(
                {"error": "Assets ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Assets.objects.get(id=id)
            obj.delete()
            return Response(
                {"message": "Assets date deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Assets.DoesNotExist:
            return Response(
                {"error": "Assets date not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
