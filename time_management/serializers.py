
# ### serializers.py
# from rest_framework import serializers
# from .models import Employee, Project, TimeSheet, TimeOff

# class EmployeeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Employee
#         fields = '__all__'

# class ProjectSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Project
#         fields = '__all__'

# class TimeSheetSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TimeSheet
#         fields = '__all__'

# class TimeOffSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TimeOff
#         fields = '__all__'


from rest_framework import serializers
from .models import User, Employee, Hierarchy, Project, Task, LeavesAvailable, LeavesTaken, ProjectAssignment, TaskAssignment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class HierarchySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hierarchy
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class LeavesAvailableSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavesAvailable
        fields = '__all__'

class LeavesTakenSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavesTaken
        fields = '__all__'

class ProjectAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAssignment
        fields = '__all__'

class TaskAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAssignment
        fields = '__all__'


