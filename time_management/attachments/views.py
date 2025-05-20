# views/attachment_views.py

from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from time_management.models import Attachment
from time_management.attachments.serializers import AttachmentSerializer


@api_view(["GET", "POST"])
@parser_classes([MultiPartParser, FormParser])
def attachment_list_create(request):
    if request.method == "GET":
        attachments = Attachment.objects.all()
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = AttachmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# views/attachment_views.py (continued)


@api_view(["GET", "DELETE"])
def attachment_detail(request, pk=None):
    if pk:
        try:
            attachment = Attachment.objects.get(pk=pk)
        except Attachment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == "GET":
            serializer = AttachmentSerializer(attachment)
            return Response(serializer.data)

        elif request.method == "DELETE":
            attachment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def attachments_by_task(request, task_id=None):
    if task_id:
        attachments = Attachment.objects.filter(task__task_id=task_id)
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data)

    else:
        attachments = Attachment.objects.all()
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def attachments_by_task_assign(request, task_assign_id=None):
    if task_assign_id:
        attachments = Attachment.objects.filter(
            task_assign__task_assign_id=task_assign_id
        )
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data)

    else:
        attachments = Attachment.objects.all()
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def attachments_by_employee(request, employee_id=None):
    if employee_id:

        attachments = Attachment.objects.filter(employee__employee_id=employee_id)
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data)

    else:
        attachments = Attachment.objects.all()
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def attachments_by_leavestaken(request, leave_taken_id=None):

    if leave_taken_id:

        attachments = Attachment.objects.filter(
            leavestaken__leave_taken_id=leave_taken_id
        )
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data)

    else:
        attachments = Attachment.objects.all()
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def attachments_by_project(request, project_id=None):

    if project_id:

        attachments = Attachment.objects.filter(project__project_id=project_id)
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data)

    else:
        attachments = Attachment.objects.all()
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data)
