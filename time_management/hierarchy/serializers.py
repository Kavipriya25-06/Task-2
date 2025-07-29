from rest_framework import serializers
from ..models import Employee, Hierarchy


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"


class HierarchySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hierarchy
        fields = "__all__"


#### The Very important helper function to get employee object under a manager upto 2 levels
#### Helper function
def emp_under_manager(emp_id):
    try:
        manager = Employee.objects.get(employee_id=emp_id)
    except Employee.DoesNotExist:
        return None

    teamleads_data = []
    employee_list = []

    # filtering all employees in the hierarchy table who reports to the manager
    teamleads_qs = Hierarchy.objects.filter(reporting_to=manager)

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
            employee_list.append(employee_emp)

        teamleads_data.append(teamlead_emp)

    # Combining teamleads_data and employees_data // This is a list of employee objects
    all_employees = teamleads_data + employee_list
    ## returning the employee objects
    return all_employees


def get_all_subordinates(manager, visited=None):

    if visited is None:
        visited = set()

    subordinates = []
    direct_reports = Hierarchy.objects.filter(reporting_to=manager)

    for hierarchy_entry in direct_reports:
        employee = hierarchy_entry.employee
        if employee.employee_id in visited:
            continue  # Prevent infinite recursion
        visited.add(employee.employee_id)

        subordinates.append(employee)
        # Recursive call for each direct report
        subordinates.extend(get_all_subordinates(employee, visited))

    return subordinates


def get_emp_under_manager(emp_id):
    try:
        manager = Employee.objects.get(employee_id=emp_id)
    except Employee.DoesNotExist:
        return []

    return get_all_subordinates(manager)


class EmployeeChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "employee_name",
            "designation",
            "department",
            "reporting_manager",
            "second_reporting_manager",
            "profile_picture",
        ]


class HierarchyChartSerializer(serializers.ModelSerializer):
    employee = EmployeeChartSerializer()
    reporting_to = EmployeeChartSerializer()
    second_reporting_to = EmployeeChartSerializer()

    class Meta:
        model = Hierarchy
        fields = ["hierarchy_id", "employee", "reporting_to", "second_reporting_to"]


# utils.py
def build_tree(manager_id, employees_map):
    children = []
    for emp in employees_map.get(manager_id, []):
        children.append(
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
    return children
