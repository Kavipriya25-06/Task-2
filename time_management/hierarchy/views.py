from rest_framework.viewsets import ModelViewSet
from ..models import Employee, Hierarchy, User
from time_management.hierarchy.serializers import (
    EmployeeSerializer,
    HierarchySerializer,
    EmployeeChartSerializer,
    HierarchyChartSerializer,
    emp_under_manager,
    get_emp_under_manager,
    build_tree,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from collections import deque


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def hierarchy_api(request, hierarchy_id=None):
    if request.method == "GET":
        if hierarchy_id:
            try:
                obj = Hierarchy.objects.get(hierarchy_id=hierarchy_id)
                serializer = HierarchySerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Hierarchy.DoesNotExist:
                return Response(
                    {"error": "Hierarchy record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = Hierarchy.objects.all()
            serializer = HierarchySerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = HierarchySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Hierarchy created", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not hierarchy_id:
            return Response(
                {"error": "Hierarchy ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Hierarchy.objects.get(hierarchy_id=hierarchy_id)
        except Hierarchy.DoesNotExist:
            return Response(
                {"error": "Hierarchy record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = HierarchySerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Hierarchy updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not hierarchy_id:
            return Response(
                {"error": "Hierarchy ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = Hierarchy.objects.get(hierarchy_id=hierarchy_id)
            obj.delete()
            return Response(
                {"message": "Hierarchy deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Hierarchy.DoesNotExist:
            return Response(
                {"error": "Hierarchy record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["GET"])
def get_emp_all(request, manager_id=None):
    try:
        manager = Employee.objects.get(employee_id=manager_id)
    except Employee.DoesNotExist:
        return Response({"error": "Manager not found"}, status=404)

    all_employee = get_emp_under_manager(manager)

    teamleads_data = []
    direct_employees = []

    for teamlead_emp in all_employee:
        # teamlead_emp = Employee.objects.get(employee_id=employee)
        reporting_to = Hierarchy.objects.filter(employee=teamlead_emp).first()
        reporting_name = (
            reporting_to.reporting_to.employee_name
            if reporting_to and reporting_to.reporting_to
            else None
        )
        teamleads_data.append(
            {
                "teamlead_id": teamlead_emp.employee_id,
                "teamlead_name": teamlead_emp.employee_name,
                "teamlead_role": teamlead_emp.designation,
                "employee_code": teamlead_emp.employee_code,
                "reporting_to": reporting_name,
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
def manager_hierarchy(request, manager_id=None):
    try:
        manager = Employee.objects.get(employee_id=manager_id)
    except Employee.DoesNotExist:
        return Response({"error": "Manager not found"}, status=404)

    teamleads_data = []
    direct_employees = []

    teamleads_qs = Hierarchy.objects.filter(reporting_to=manager)

    for tl_hierarchy in teamleads_qs:
        teamlead_emp = tl_hierarchy.employee
        user_qs = User.objects.filter(employee_id=teamlead_emp).first()

        if user_qs and user_qs.role == "teamlead":
            # This employee is a teamlead, get their employees
            employees_qs = Hierarchy.objects.filter(reporting_to=teamlead_emp)
            employee_list = [
                {
                    "employee_id": emp_h.employee.employee_id,
                    "employee_name": emp_h.employee.employee_name,
                    "employee_code": emp_h.employee.employee_code,
                }
                for emp_h in employees_qs
            ]

            teamleads_data.append(
                {
                    "teamlead_id": teamlead_emp.employee_id,
                    "teamlead_name": teamlead_emp.employee_name,
                    "employee_code": teamlead_emp.employee_code,
                    "employees": employee_list,
                }
            )
        else:
            # This employee is not a teamlead, add to manager's direct employees
            direct_employees.append(
                {
                    "employee_id": teamlead_emp.employee_id,
                    "employee_name": teamlead_emp.employee_name,
                    "employee_code": teamlead_emp.employee_code,
                }
            )

    response = {
        "manager_id": manager.employee_id,
        "manager_name": manager.employee_name,
        "employees": direct_employees,
        "teamleads": teamleads_data,
    }

    return Response(response)


@api_view(["GET"])
def teamlead_hierarchy(request, emp_id=None):
    try:
        teamlead = Employee.objects.get(employee_id=emp_id)
    except Employee.DoesNotExist:
        return Response({"error": "Team Lead not found"}, status=404)

    # Get all employees reporting to this teamlead
    reporting_employees = Hierarchy.objects.filter(reporting_to=teamlead)

    employees = [
        {
            "employee_id": h.employee.employee_id,
            "employee_name": h.employee.employee_name,
            "employee_code": h.employee.employee_code,
        }
        for h in reporting_employees
    ]

    response = {
        "teamlead_id": teamlead.employee_id,
        "teamlead_name": teamlead.employee_name,
        "employee_code": teamlead.employee_code,
        "employees": employees,
    }

    return Response(response)


@api_view(["GET"])
def org_hierarchy(request, emp_id=None):
    try:
        manager = Employee.objects.get(employee_id=emp_id)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)

    teamleads_data = []
    direct_employees = []

    # filtering all employees in the hierarchy table who reports to the manager
    teamleads_qs = Hierarchy.objects.filter(reporting_to=manager)

    # iterating through each filtered hierarchy table entry
    for tl_hierarchy in teamleads_qs:
        teamlead_emp = (
            tl_hierarchy.employee
        )  # getting the employee id from the filtered hierarchy table
        user_qs = User.objects.filter(
            employee_id=teamlead_emp
        ).first()  # matching the employee id in user table

        if user_qs:
            # This employee, get their employees
            employees_qs = Hierarchy.objects.filter(reporting_to=teamlead_emp)
            employee_list = [
                {
                    "employee_id": emp_h.employee.employee_id,
                    "employee_name": emp_h.employee.employee_name,
                    "employee_role": emp_h.employee.designation,
                    "employee_code": emp_h.employee.employee_code,
                }
                for emp_h in employees_qs
            ]

            teamleads_data.append(
                {
                    "teamlead_id": teamlead_emp.employee_id,
                    "teamlead_name": teamlead_emp.employee_name,
                    "teamlead_role": teamlead_emp.designation,
                    "employee_code": teamlead_emp.employee_code,
                    "employees": employee_list,
                }
            )
        else:
            # This employee is not a teamlead, add to manager's direct employees
            direct_employees.append(
                {
                    "employee_id": teamlead_emp.employee_id,
                    "employee_name": teamlead_emp.employee_name,
                    "employee_role": teamlead_emp.designation,
                    "employee_code": teamlead_emp.employee_code,
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
def teamleads_under_manager(request, manager_id):
    try:
        # Get the manager's employee record
        manager = Employee.objects.get(employee_id=manager_id)
    except Employee.DoesNotExist:
        return Response(
            {"error": "Manager not found"}, status=status.HTTP_404_NOT_FOUND
        )

    # Get all team leads that report to the manager
    teamleads = Hierarchy.objects.filter(reporting_to=manager)

    # Prepare the list of team leads with their employees
    teamlead_data = []
    for teamlead in teamleads:
        teamlead_emp = teamlead.employee  # The team lead employee object

        # Get employees reporting to this team lead
        employees = Hierarchy.objects.filter(reporting_to=teamlead_emp)

        # Add the team lead data with the associated employees
        teamlead_data.append(
            {
                "teamlead_id": teamlead_emp.employee_id,
                "teamlead_name": teamlead_emp.employee_name,
                "employee_code": teamlead_emp.employee_code,
                "employees": [
                    {
                        "employee_id": emp.employee.employee_id,
                        "employee_name": emp.employee.employee_name,
                        "employee_code": emp.employee.employee_code,
                    }
                    for emp in employees
                ],
            }
        )

    # Return the data as a response
    return Response(teamlead_data)


@api_view(["GET"])
def get_hierarchy_by_employee(request, employee_id):
    if employee_id:
        try:
            hierarchy = Hierarchy.objects.get(employee__employee_id=employee_id)
            serializer = HierarchySerializer(hierarchy)
            return Response(serializer.data, status=200)
        except Hierarchy.DoesNotExist:
            return Response({"error": "No hierarchy found"}, status=404)
    else:
        return Response({"error": "No employee found"}, status=404)


# @api_view(["GET"])
# def manager_chart(request):
#     employees = Employee.objects.all()
#     tree = {}

#     # Build tree structure { manager_id: [subordinates] }
#     for emp in employees:
#         manager_id = emp.reporting_manager
#         if not manager_id:
#             continue
#         if manager_id not in tree:
#             tree[manager_id] = []
#         tree[manager_id].append(
#             {
#                 "id": emp.employee_id,
#                 "name": emp.employee_name,
#                 "designation": emp.designation,
#                 "department": emp.department,
#                 "profile_picture": (
#                     emp.profile_picture.url if emp.profile_picture else None
#                 ),
#             }
#         )

#     return Response(tree)


@api_view(["GET"])
def manager_chart(request):
    employees = Employee.objects.all()

    # Map of manager_id → list of subordinates
    employees_map = {}
    for emp in employees:
        if emp.reporting_manager:
            employees_map.setdefault(emp.reporting_manager, []).append(emp)

    # Build tree starting at each manager (with subordinates)
    managers_data = {}
    for manager_id, subordinates in employees_map.items():
        try:
            manager = Employee.objects.get(employee_id=manager_id)
        except Employee.DoesNotExist:
            continue

        managers_data[manager_id] = {
            "manager": {
                "id": manager.employee_id,
                "name": manager.employee_name,
                "designation": manager.designation,
                "profile_picture": (
                    manager.profile_picture.url if manager.profile_picture else None
                ),
            },
            "children": [
                {
                    "id": emp.employee_id,
                    "name": emp.employee_name,
                    "designation": emp.designation,
                    "profile_picture": (
                        emp.profile_picture.url if emp.profile_picture else None
                    ),
                    "children": build_tree(emp.employee_id, employees_map),
                }
                for emp in subordinates
            ],
        }

    return Response(managers_data)


@api_view(["GET"])
def department_chart(request):
    employees = Employee.objects.all()
    departments = {}

    # Map: manager_id → [subordinates]
    employees_map = {}
    for emp in employees:
        if emp.reporting_manager:
            employees_map.setdefault(emp.reporting_manager, []).append(emp)

    # Find top-level employees in each department (no manager or manager in another dept)
    for emp in employees:
        dept = emp.department or "Unassigned"
        if dept not in departments:
            departments[dept] = []

        if not emp.reporting_manager:  # top-level node
            departments[dept].append(
                {
                    "id": emp.employee_id,
                    "name": emp.employee_name,
                    "designation": emp.designation,
                    "profile_picture": (
                        emp.profile_picture.url if emp.profile_picture else None
                    ),
                    "children": build_tree(emp.employee_id, employees_map),
                }
            )

    return Response(departments)


# @api_view(["GET"])
# def org_hierarchy(request, emp_id=None):
#     try:
#         manager = Employee.objects.get(employee_id=emp_id)
#     except Employee.DoesNotExist:
#         return Response({"error": "Employee not found"}, status=404)

#     def get_reporting_employees(manager):
#         """
#         Helper function to recursively get all employees reporting to a manager.
#         """
#         teamleads_data = []
#         direct_employees = []

#         # Get team leads reporting to this manager
#         teamleads_qs = Hierarchy.objects.filter(reporting_to=manager)

#         for tl_hierarchy in teamleads_qs:
#             teamlead_emp = tl_hierarchy.employee
#             user_qs = User.objects.filter(employee_id=teamlead_emp).first()

#             if user_qs:
#                 # This employee is a teamlead, so recursively get their employees
#                 employees_qs = get_reporting_employees(teamlead_emp)

#                 teamleads_data.append(
#                     {
#                         "teamlead_id": teamlead_emp.employee_id,
#                         "teamlead_name": teamlead_emp.employee_name,
#                         "employees": employees_qs,
#                     }
#                 )
#             else:
#                 # This employee is not a teamlead, add them as a direct employee
#                 direct_employees.append(
#                     {
#                         "employee_id": teamlead_emp.employee_id,
#                         "employee_name": teamlead_emp.employee_name,
#                     }
#                 )

#         return {
#             "teamleads": teamleads_data,
#             "employees": direct_employees,
#         }

#     # Get the reporting structure of the manager
#     hierarchy_data = get_reporting_employees(manager)

#     # Construct the response
#     response = {
#         "manager_id": manager.employee_id,
#         "manager_name": manager.employee_name,
#         **hierarchy_data,
#     }

#     return Response(response)


# @api_view(["GET"])
# def org_hierarchy(request, emp_id=None):
#     try:
#         manager = Employee.objects.get(employee_id=emp_id)
#     except Employee.DoesNotExist:
#         return Response({"error": "Employee not found"}, status=404)

#     teamleads_data = []
#     direct_employees = []
#     processed_employees = set()  # To track already processed employees

#     # Create a queue to hold the managers and their direct reports
#     queue = deque([manager])

#     while queue:
#         current_manager = queue.popleft()

#         # Get team leads reporting to the current manager
#         teamleads_qs = Hierarchy.objects.filter(reporting_to=current_manager)

#         for tl_hierarchy in teamleads_qs:
#             teamlead_emp = tl_hierarchy.employee
#             user_qs = User.objects.filter(employee_id=teamlead_emp).first()

#             if user_qs:
#                 # This employee is a teamlead, so we add them to the queue to fetch their employees
#                 # Check if this teamlead has already been processed
#                 if teamlead_emp.employee_id not in processed_employees:
#                     employees_qs = Hierarchy.objects.filter(reporting_to=teamlead_emp)
#                     employee_list = [
#                         {
#                             "employee_id": emp_h.employee.employee_id,
#                             "employee_name": emp_h.employee.employee_name,
#                         }
#                         for emp_h in employees_qs
#                     ]

#                     teamleads_data.append(
#                         {
#                             "teamlead_id": teamlead_emp.employee_id,
#                             "teamlead_name": teamlead_emp.employee_name,
#                             "employees": employee_list,
#                         }
#                     )
#                     # Add the team lead to the queue to fetch their reports
#                     queue.append(teamlead_emp)
#                     processed_employees.add(teamlead_emp.employee_id)
#             else:
#                 # This employee is not a teamlead, add to direct employees under the current manager
#                 if teamlead_emp.employee_id not in processed_employees:
#                     direct_employees.append(
#                         {
#                             "employee_id": teamlead_emp.employee_id,
#                             "employee_name": teamlead_emp.employee_name,
#                         }
#                     )
#                     processed_employees.add(teamlead_emp.employee_id)

#     response = {
#         "manager_id": manager.employee_id,
#         "manager_name": manager.employee_name,
#         "teamleads": teamleads_data,
#         "employees": direct_employees,
#     }

#     return Response(response)


# ### new one
# @api_view(["GET"])
# def org_hierarchy(request, emp_id=None):
#     try:
#         manager = Employee.objects.get(employee_id=emp_id)
#     except Employee.DoesNotExist:
#         return Response({"error": "Employee not found"}, status=404)

#     hierarchy_data = []

#     # Create a queue to hold the managers and their direct reports
#     queue = deque([manager])

#     while queue:
#         current_manager = queue.popleft()

#         # Get team leads reporting to the current manager
#         teamleads_qs = Hierarchy.objects.filter(reporting_to=current_manager)

#         teamleads = []

#         for tl_hierarchy in teamleads_qs:
#             teamlead_emp = tl_hierarchy.employee
#             user_qs = User.objects.filter(employee_id=teamlead_emp).first()

#             # Initialize the team lead data
#             teamlead_data = {
#                 "teamlead_id": teamlead_emp.employee_id,
#                 "teamlead_name": teamlead_emp.employee_name,
#                 "employees": [],
#             }

#             if user_qs:
#                 # This employee is a team lead, so we add them to the hierarchy
#                 employees_qs = Hierarchy.objects.filter(reporting_to=teamlead_emp)
#                 for emp_hierarchy in employees_qs:
#                     employee = emp_hierarchy.employee
#                     teamlead_data["employees"].append(
#                         {
#                             "employee_id": employee.employee_id,
#                             "employee_name": employee.employee_name,
#                         }
#                     )

#                 # Add the team lead to the queue to fetch their employees
#                 queue.append(teamlead_emp)

#             # Add teamlead to teamleads list
#             teamleads.append(teamlead_data)

#         # Append the current manager with their team leads to the hierarchy
#         hierarchy_data.append(
#             {
#                 "manager_id": current_manager.employee_id,
#                 "manager_name": current_manager.employee_name,
#                 "teamleads": teamleads,
#             }
#         )

#     return Response(hierarchy_data)
