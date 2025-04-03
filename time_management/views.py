from django.shortcuts import render

# Create your views here.
### views.py
from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework import status
# from .models import Employee, Project, TimeSheet, TimeOff
# from .serializers import EmployeeSerializer, ProjectSerializer, TimeSheetSerializer, TimeOffSerializer

# class EmployeeListCreate(APIView):
#     def get(self, request):
#         employees = Employee.objects.all()
#         serializer = EmployeeSerializer(employees, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = EmployeeSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class ProjectListCreate(APIView):
#     def get(self, request):
#         projects = Project.objects.all()
#         serializer = ProjectSerializer(projects, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = ProjectSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class TimeSheetListCreate(APIView):
#     def get(self, request):
#         timesheets = TimeSheet.objects.all()
#         serializer = TimeSheetSerializer(timesheets, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = TimeSheetSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class TimeOffListCreate(APIView):
#     def get(self, request):
#         time_offs = TimeOff.objects.all()
#         serializer = TimeOffSerializer(time_offs, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = TimeOffSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import viewsets
from .models import *
from .serializers import *

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
