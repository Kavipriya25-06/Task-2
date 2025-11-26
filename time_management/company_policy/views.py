from ..models import CompanyPolicy
from time_management.company_policy.serializers import (
    CompanyPolicySerializer,
    CompanyPolicyViewSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
@parser_classes([MultiPartParser, FormParser])
def company_policy_api(request, id=None):
    if request.method == "GET":

        if id:
            try:
                obj = CompanyPolicy.objects.get(id=id)
                serializer = CompanyPolicyViewSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except CompanyPolicy.DoesNotExist:
                return Response(
                    {"error": "CompanyPolicy date not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = CompanyPolicy.objects.all()
            serializer = CompanyPolicyViewSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        # Copy data so we can inject uploaded_by
        mutable_data = request.data.copy()
        # If you have Employee linked to User
        # employee = getattr(request.data, "employee", None)
        employee = request.data.get("employee", None)
        print("Employee", employee)
        if employee:
            mutable_data["uploaded_by"] = employee

        serializer = CompanyPolicySerializer(data=mutable_data)
        if serializer.is_valid():
            serializer.save()
            # For frontend simplicity, return the created object directly
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not id:
            return Response(
                {"error": "CompanyPolicy ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = CompanyPolicy.objects.get(id=id)
        except CompanyPolicy.DoesNotExist:
            return Response(
                {"error": "CompanyPolicy data not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CompanyPolicySerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "CompanyPolicy date updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not id:
            return Response(
                {"error": "CompanyPolicy ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = CompanyPolicy.objects.get(id=id)
            obj.delete()
            return Response(
                {"message": "CompanyPolicy date deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except CompanyPolicy.DoesNotExist:
            return Response(
                {"error": "CompanyPolicy date not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
