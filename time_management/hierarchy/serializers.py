from rest_framework import serializers
from ..models import Employee, Hierarchy

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class HierarchySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hierarchy
        fields = '__all__'


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
