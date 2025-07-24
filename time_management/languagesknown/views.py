from ..models import LanguagesKnown
from time_management.languagesknown.serializers import LanguagesKnownSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def languages_known_api(request, id=None):
    if request.method == "GET":

        if id:
            try:
                obj = LanguagesKnown.objects.get(id=id)
                serializer = LanguagesKnownSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except LanguagesKnown.DoesNotExist:
                return Response(
                    {"error": "LanguagesKnown date not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = LanguagesKnown.objects.all()
            serializer = LanguagesKnownSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = LanguagesKnownSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "LanguagesKnown data added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not id:
            return Response(
                {"error": "LanguagesKnown ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = LanguagesKnown.objects.get(id=id)
        except LanguagesKnown.DoesNotExist:
            return Response(
                {"error": "LanguagesKnown data not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LanguagesKnownSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "LanguagesKnown date updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not id:
            return Response(
                {"error": "LanguagesKnown ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = LanguagesKnown.objects.get(id=id)
            obj.delete()
            return Response(
                {"message": "LanguagesKnown date deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except LanguagesKnown.DoesNotExist:
            return Response(
                {"error": "LanguagesKnown date not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
