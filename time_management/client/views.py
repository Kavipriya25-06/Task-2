from rest_framework.viewsets import ModelViewSet
from ..models import (
    Client,
    ClientPOC,
)

from time_management.client.serializers import ClientSerializer, ClientPOCSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from time_management.hierarchy.serializers import get_emp_under_manager


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def client_api(request, id=None):
    if request.method == "GET":

        if id:
            try:
                obj = Client.objects.get(id=id)
                serializer = ClientSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Client.DoesNotExist:
                return Response(
                    {"error": "Client date not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = Client.objects.all()
            serializer = ClientSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Client date added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not id:
            return Response(
                {"error": "Client ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Client.objects.get(id=id)
        except Client.DoesNotExist:
            return Response(
                {"error": "Client date not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ClientSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Client date updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not id:
            return Response(
                {"error": "Client ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Client.objects.get(id=id)
            obj.delete()
            return Response(
                {"message": "Client date deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Client.DoesNotExist:
            return Response(
                {"error": "Client date not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def client_poc_api(request, id=None):
    if request.method == "GET":
        if id:
            try:
                obj = ClientPOC.objects.get(id=id)
                serializer = ClientPOCSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ClientPOC.DoesNotExist:
                return Response(
                    {"error": "Leave record with leave id not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        else:
            objs = ClientPOC.objects.all()
            serializer = ClientPOCSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = ClientPOCSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Leave balance created", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not id:
            return Response(
                {"error": "Leave record ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = ClientPOC.objects.get(id=id)
        except ClientPOC.DoesNotExist:
            return Response(
                {"error": "Leave record not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClientPOCSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Leave balance updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not id:
            return Response(
                {"error": "Leave record ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = ClientPOC.objects.get(id=id)
            obj.delete()
            return Response(
                {"message": "Leave balance deleted"}, status=status.HTTP_204_NO_CONTENT
            )
        except ClientPOC.DoesNotExist:
            return Response(
                {"error": "Leave record not found"}, status=status.HTTP_404_NOT_FOUND
            )
