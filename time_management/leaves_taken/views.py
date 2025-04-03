from rest_framework.viewsets import ModelViewSet
from ..models import LeavesTaken
from time_management.leaves_taken.serializers import LeavesTakenSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def leaves_taken_api(request, leave_taken_id=None):
    if request.method == "GET":
        if leave_taken_id:
            try:
                obj = LeavesTaken.objects.get(leave_taken_id=leave_taken_id)
                serializer = LeavesTakenSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except LeavesTaken.DoesNotExist:
                return Response(
                    {"error": "Leave record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = LeavesTaken.objects.all()
            serializer = LeavesTakenSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = LeavesTakenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Leave request submitted", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not leave_taken_id:
            return Response(
                {"error": "Leave record ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = LeavesTaken.objects.get(leave_taken_id=leave_taken_id)
        except LeavesTaken.DoesNotExist:
            return Response(
                {"error": "Leave record not found"}, status=status.HTTP_404_NOT_FOUND
            )

        status_update = request.data.get("status")
        if status_update and status_update not in ["pending", "approved", "rejected"]:
            return Response(
                {"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = LeavesTakenSerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Leave request updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not leave_taken_id:
            return Response(
                {"error": "Leave record ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = LeavesTaken.objects.get(leave_taken_id=leave_taken_id)
            obj.delete()
            return Response(
                {"message": "Leave request deleted"}, status=status.HTTP_204_NO_CONTENT
            )
        except LeavesTaken.DoesNotExist:
            return Response(
                {"error": "Leave record not found"}, status=status.HTTP_404_NOT_FOUND
            )
