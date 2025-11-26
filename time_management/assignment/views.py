from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ..models import (
    Project,
    ProjectAssign,
    Building,
    BuildingAssign,
    Task,
    TaskAssign,
    Hierarchy,
    Employee,
    User,
)
from time_management.assignment.serializers import (
    ProjectSerializer,
    ProjectViewSerializer,
    ProjectAssignSerializer,
    EmployeeSerializer,
    HierarchySerializer,
)


@api_view(["GET"])
def manager_team_leads(request, manager_id=None):
    try:
        manager = Employee.objects.get(employee_id=manager_id)
    except Employee.DoesNotExist:
        return Response({"error": "Manager not found"}, status=404)

    # Get all Team Leads reporting to this manager
    teamleads_qs = Hierarchy.objects.filter(reporting_to=manager)

    teamleads_data = []
    for teamlead_hierarchy in teamleads_qs:
        teamlead_emp = teamlead_hierarchy.employee
        # Get the projects assigned to this team lead
        project_assignments = ProjectAssign.objects.filter(employee=teamlead_emp)
        # Count of projects assigned
        total_projects = project_assignments.count()

        completed_count = project_assignments.filter(status="completed")

        inprogress_count = project_assignments.filter(status="inprogress")

        pending_count = project_assignments.filter(status="pending")

        # Get the employees under this team lead
        employees_qs = Hierarchy.objects.filter(reporting_to=teamlead_emp)
        total_employees = employees_qs.count()

        teamleads_data.append(
            {
                "teamlead_id": teamlead_emp.employee_id,
                "teamlead_name": teamlead_emp.employee_name,
                "total_projects": total_projects,
                "completed_count": completed_count,
                "inprogress_count": inprogress_count,
                "pending_count": pending_count,
                "total_employees": total_employees,
            }
        )

    return Response(
        {
            "manager_id": manager.employee_id,
            "manager_name": manager.employee_name,
            "teamleads": teamleads_data,
        }
    )


@api_view(["GET"])
def manager_tl_projects(request, employee_id=None):
    try:
        manager = Employee.objects.get(employee_id=employee_id)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)

    teamleads_data = []
    direct_employees = []

    # filtering all employees in the hierarchy table who reports to the manager
    teamleads_qs = Hierarchy.objects.filter(
        reporting_to=manager, employee__status="active"
    )

    # iterating through each filtered hierarchy table entry
    for tl_hierarchy in teamleads_qs:
        teamlead_emp = (
            tl_hierarchy.employee
        )  # getting the employee id from the filtered hierarchy table
        # Get the projects assigned to this team lead
        project_assignments = ProjectAssign.objects.filter(employee=teamlead_emp)
        # Count of projects assigned
        total_projects = project_assignments.count()

        completed_projects = project_assignments.filter(status="completed").count()
        inprogress_projects = project_assignments.filter(status="inprogress").count()
        pending_projects = project_assignments.filter(status="pending").count()

        user_qs = User.objects.filter(
            employee_id=teamlead_emp, status="active"
        ).first()  # matching the employee id in user table

        if user_qs and user_qs.role == "teamlead":
            # This employee, get their employees
            employees_qs = Hierarchy.objects.filter(
                reporting_to=teamlead_emp, employee__status="active"
            )
            total_employees = employees_qs.count()
            employee_list = [
                {
                    "employee_id": emp_h.employee.employee_id,
                    "employee_name": emp_h.employee.employee_name,
                }
                for emp_h in employees_qs
            ]

            teamleads_data.append(
                {
                    "teamlead_id": teamlead_emp.employee_id,
                    "teamlead_name": teamlead_emp.employee_name,
                    "last_name": teamlead_emp.last_name,
                    "employees": employee_list,
                    "total_employees": total_employees,
                    "total_projects": total_projects,
                    "completed_count": completed_projects,
                    "inprogress_count": inprogress_projects,
                    "pending_count": pending_projects,
                }
            )
        else:
            continue
            # This employee is not a teamlead, add to manager's direct employees
            teamleads_data.append(
                {
                    "employee_id": teamlead_emp.employee_id,
                    "employee_name": teamlead_emp.employee_name,
                    "total_projects": total_projects,
                    "completed_count": completed_projects,
                    "inprogress_count": inprogress_projects,
                    "pending_count": pending_projects,
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
def tl_projects(request, employee_id=None):
    try:
        # Fetch the employee by employee_id
        employee = Employee.objects.get(employee_id=employee_id)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)

    # Fetch all Project Assignments where the employee is assigned
    project_assignments = ProjectAssign.objects.filter(employee=employee)

    # Serialize the projects assigned to the employee
    projects = ProjectAssignSerializer(project_assignments, many=True)

    # Return the serialized data as a response
    return Response(projects.data)
