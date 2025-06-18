from django.db.models import Q
from ..models import Employee, Hierarchy, User
from time_management.employee.serializers import (
    EmployeeSerializer,
    HierarchySerializer,
    UserSerializer,
    EmployeeViewSerializer,
)
from time_management.hierarchy.serializers import (
    emp_under_manager,
    get_emp_under_manager,
)
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
# @parser_classes([MultiPartParser, FormParser])
def employee_api(request, employee_id=None):
    # GET (single or list)
    if request.method == "GET":
        if employee_id:
            try:
                employee = Employee.objects.get(employee_id=employee_id)
                serializer = EmployeeSerializer(employee)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Employee.DoesNotExist:
                return Response(
                    {"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
                )
        else:
            employees = Employee.objects.all()
            serializer = EmployeeSerializer(employees, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    # POST
    if request.method == "POST":
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Employee created", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "error": "Employee creation failed",
                    "details": serializer.errors,
                },
                status=400,
            )

        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT (full update)
    if request.method == "PUT":
        if not employee_id:
            return Response(
                {"error": "Employee ID is required for PUT"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = EmployeeSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Employee updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                {
                    "error": "Employee update failed",
                    "details": serializer.errors,
                },
                status=400,
            )
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH (partial update)
    if request.method == "PATCH":
        if not employee_id:
            return Response(
                {"error": "Employee ID is required for PATCH"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Employee partially updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "error": "Employee update failed",
                    "details": serializer.errors,
                },
                status=400,
            )
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    if request.method == "DELETE":
        if not employee_id:
            return Response(
                {"error": "Employee ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            employee = Employee.objects.get(employee_id=employee_id)
            employee.delete()
            return Response(
                {"message": "Employee deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
            )


@api_view(["GET"])
# @parser_classes([MultiPartParser, FormParser])
def employee_view_api(request, employee_id=None):
    # GET (single or list)
    if request.method == "GET":
        if employee_id:
            try:
                employee = Employee.objects.get(employee_id=employee_id)
                serializer = EmployeeViewSerializer(employee)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Employee.DoesNotExist:
                return Response(
                    {"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
                )
        else:
            employees = Employee.objects.all()
            serializer = EmployeeViewSerializer(employees, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def unassigned_employee(request):

    user_ids = User.objects.exclude(employee_id__isnull=True)
    user_employee_ids = user_ids.values_list("employee_id", flat=True)
    print("Users", user_employee_ids)

    # employees = Employee.objects.exclude(employee_id__in=user_employee_ids)
    employees = Employee.objects.exclude(
        Q(employee_id__in=user_employee_ids)
        | Q(employee_email__isnull=True)
        | Q(employee_email__exact="")
    )
    serializer = EmployeeViewSerializer(employees, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
# @parser_classes([MultiPartParser, FormParser])
def emp_under_mngr_view(request, employee_id=None):
    # GET (single or list)
    """
    This gives the Employee details of all the employees and team leads under a manager up to 2 levels
    """
    if request.method == "GET":
        if employee_id:
            try:
                manager = Employee.objects.get(employee_id=employee_id)
                employees = get_emp_under_manager(manager)
                employee = Employee.objects.filter(employee_id__in=employees)
                serializer = EmployeeViewSerializer(employee, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Employee.DoesNotExist:
                return Response(
                    {"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
                )

        else:
            employees = Employee.objects.all()
            serializer = EmployeeViewSerializer(employees, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
# @parser_classes([MultiPartParser, FormParser])
def mntl_view_api(request, employee_id=None):
    # GET (single or list)
    if request.method == "GET":
        # Filter employees based on roles 'teamlead' or 'manager'
        employees_qs = Employee.objects.filter(user__role__in=["teamlead", "manager"])
        if employee_id:
            try:
                employee = Employee.objects.get(employee_id=employee_id)
                serializer = EmployeeViewSerializer(employees_qs)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Employee.DoesNotExist:
                return Response(
                    {"error": "Manager or TeamLead not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            employees = Employee.objects.all()
            serializer = EmployeeViewSerializer(employees_qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
