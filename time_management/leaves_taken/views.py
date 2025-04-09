from rest_framework.viewsets import ModelViewSet
from ..models import LeavesTaken, Employee, Hierarchy, User
from time_management.leaves_taken.serializers import (
    LeavesTakenSerializer,
    LeaveRequestSerializer,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime


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


@api_view(["GET"])
def org_leaves(request, employee_id=None):
    try:
        # Fetch the manager by emp_id
        manager = Employee.objects.get(employee_id=employee_id)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)

    teamleads_data = []
    direct_employees = []

    # Filtering all employees in the hierarchy table who report to the manager
    teamleads_qs = Hierarchy.objects.filter(reporting_to=manager)

    # Iterating through each filtered hierarchy entry to get team leads and their employees
    for tl_hierarchy in teamleads_qs:
        teamlead_emp = (
            tl_hierarchy.employee
        )  # Getting the employee from hierarchy table
        user_qs = User.objects.filter(
            employee_id=teamlead_emp
        ).first()  # Get the user info

        if user_qs:
            # This employee is a teamlead, get their employees
            employees_qs = Hierarchy.objects.filter(reporting_to=teamlead_emp)
            employee_list = []

            for emp_h in employees_qs:
                employee = emp_h.employee
                # Get leaves taken by this employee
                leaves_taken = LeavesTaken.objects.filter(employee=employee)
                leaves_data = [
                    {
                        "leave_taken_id": leave.leave_taken_id,
                        "leave_type": leave.leave_type,
                        "start_date": leave.start_date,
                        "end_date": leave.end_date,
                        "duration": leave.duration,
                        "status": leave.status,
                    }
                    for leave in leaves_taken
                ]
                employee_list.append(
                    {
                        "employee_id": employee.employee_id,
                        "employee_name": employee.employee_name,
                        "employee_role": employee.designation,
                        "leaves_taken": leaves_data,
                    }
                )

            # This employee is not a teamlead, add to manager's direct employees
            leaves_taken = LeavesTaken.objects.filter(employee=teamlead_emp)
            leaves_data = [
                {
                    "leave_taken_id": leave.leave_taken_id,
                    "leave_type": leave.leave_type,
                    "start_date": leave.start_date,
                    "end_date": leave.end_date,
                    "duration": leave.duration,
                    "status": leave.status,
                }
                for leave in leaves_taken
            ]
            teamleads_data.append(
                {
                    "teamlead_id": teamlead_emp.employee_id,
                    "teamlead_name": teamlead_emp.employee_name,
                    "teamlead_role": teamlead_emp.designation,
                    "leaves_taken": leaves_data,
                    "employees": employee_list,
                }
            )
        else:
            # This employee is not a teamlead, add to manager's direct employees
            leaves_taken = LeavesTaken.objects.filter(employee=teamlead_emp)
            leaves_data = [
                {
                    "leave_taken_id": leave.leave_taken_id,
                    "leave_type": leave.leave_type,
                    "start_date": leave.start_date,
                    "end_date": leave.end_date,
                    "duration": leave.duration,
                    "status": leave.status,
                }
                for leave in leaves_taken
            ]
            direct_employees.append(
                {
                    "employee_id": teamlead_emp.employee_id,
                    "employee_name": teamlead_emp.employee_name,
                    "leaves_taken": leaves_data,
                }
            )

    response = {
        "manager_id": manager.employee_id,
        "manager_name": manager.employee_name,
        "teamleads": teamleads_data,
        "employees": direct_employees,
    }

    return Response(response)


@api_view(["GET"])
def leave_request_api(request, manager_id=None):
    """
    This filters the leave requests from employees under a particular manager.
    """
    if request.method == "GET":
        if manager_id:
            try:
                # Fetch the manager by emp_id
                manager = Employee.objects.get(employee_id=manager_id)

                # Filtering all employees in the hierarchy table who report to the manager
                teamleads_qs = Hierarchy.objects.filter(reporting_to=manager)

                # Initializing the response structure
                teamleads_data = []
                employees_data = []

                # Iterating through each filtered hierarchy entry to get team leads and their employees
                for tl_hierarchy in teamleads_qs:
                    teamlead_emp = (
                        tl_hierarchy.employee
                    )  # Getting the employee from hierarchy table
                    employees_qs = Hierarchy.objects.filter(reporting_to=teamlead_emp)

                    for emp_hierarchy in employees_qs:
                        employee_emp = (
                            emp_hierarchy.employee
                        )  # Getting the employee from hierarchy table
                        employees_data.append(employee_emp)

                    teamleads_data.append(teamlead_emp)

                # Combining teamleads_data and employees_data
                all_employees = teamleads_data + employees_data

                # Fetching the leave records for all team leads and employees
                leave_qs = LeavesTaken.objects.filter(employee__in=all_employees)

                serializer = LeaveRequestSerializer(leave_qs, many=True)

                return Response(serializer.data, status=status.HTTP_200_OK)
            except Employee.DoesNotExist:
                return Response(
                    {"error": "Manager not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            except LeavesTaken.DoesNotExist:
                return Response(
                    {"error": "Leave record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = LeavesTaken.objects.all()
            serializer = LeaveRequestSerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(["GET"])
# def leave_request_api(request, manager_id=None):
#     if request.method == "GET":
#         if manager_id:
#             try:
#                 # Fetch the manager by emp_id
#                 manager = Employee.objects.get(employee_id=manager_id)

#                 # Filtering all employees in the hierarchy table who report to the manager
#                 teamleads_qs = Hierarchy.objects.filter(reporting_to=manager)

#                 # Initializing the response structure
#                 teamleads_data = []
#                 employees_data = []

#                 # Iterating through each filtered hierarchy entry to get team leads and their employees
#                 for tl_hierarchy in teamleads_qs:
#                     teamlead_emp = (
#                         tl_hierarchy.employee
#                     )  # Getting the employee from hierarchy table
#                     employees_qs = Hierarchy.objects.filter(reporting_to=teamlead_emp)
#                     teamlead_leaves = LeavesTaken.objects.filter(employee=teamlead_emp)

#                     # employees_data = []
#                     for emp_hierarchy in employees_qs:
#                         employee_emp = (
#                             emp_hierarchy.employee
#                         )  # Getting the employee from hierarchy table
#                         employee_leaves = LeavesTaken.objects.filter(
#                             employee=employee_emp
#                         )
#                         employees_data.append(employee_emp)

#                     teamleads_data.append(teamlead_emp)

#                 # print(teamleads_data)
#                 # print(employees_data)
#                 teamleads_data.extend(employees_data)
#                 print(teamleads_data)

#                 # Combining teamleads_data and employees_data
#                 all_employees = teamleads_data + employees_data

#                 # Fetching the leave records for all team leads and employees
#                 leave_qs = LeavesTaken.objects.filter(employee__in=all_employees)

#                 # firstteamlead = teamleads_data[0]
#                 # print(firstteamlead)
#                 obj = LeavesTaken.objects.filter(employee=manager_id)
#                 # print(obj)
#                 print("Manager id", manager_id)
#                 final_qs = []
#                 # for emp in teamleads_data:
#                 #     leave_qs = LeavesTaken.objects.filter(employee=emp)
#                 #     # final_qs = final_qs | leave_qs
#                 #     # print(final_qs)
#                 #     print(emp)
#                 #     # print(leave_qs)
#                 # print(leave_qs)
#                 serializer = LeaveRequestSerializer(leave_qs, many=True)
#                 # serializer = LeaveRequestSerializer(obj, many=True)
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             except LeavesTaken.DoesNotExist:
#                 return Response(
#                     {"error": "Leave record not found"},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )
#         else:
#             objs = LeavesTaken.objects.all()
#             serializer = LeaveRequestSerializer(objs, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
