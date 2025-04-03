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
