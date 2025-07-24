from ..models import EmployeeAttachment
from time_management.employee_attachment.serializers import EmployeeAttachmentSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def employee_attachment_api(request, id=None):
    if request.method == "GET":

        if id:
            try:
                obj = EmployeeAttachment.objects.get(id=id)
                serializer = EmployeeAttachmentSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except EmployeeAttachment.DoesNotExist:
                return Response(
                    {"error": "EmployeeAttachment date not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = EmployeeAttachment.objects.all()
            serializer = EmployeeAttachmentSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = EmployeeAttachmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "EmployeeAttachment data added", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not id:
            return Response(
                {"error": "EmployeeAttachment ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = EmployeeAttachment.objects.get(id=id)
        except EmployeeAttachment.DoesNotExist:
            return Response(
                {"error": "EmployeeAttachment data not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EmployeeAttachmentSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "EmployeeAttachment date updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not id:
            return Response(
                {"error": "EmployeeAttachment ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = EmployeeAttachment.objects.get(id=id)
            obj.delete()
            return Response(
                {"message": "EmployeeAttachment date deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except EmployeeAttachment.DoesNotExist:
            return Response(
                {"error": "EmployeeAttachment date not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
