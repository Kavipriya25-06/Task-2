from django.contrib import admin

from .models import (
    User,
    Employee,
    Hierarchy,
    LeavesAvailable,
    LeavesTaken,
    Calendar,
    BiometricData,
    Project,
    Building,
    Task,
    ProjectAssign,
    BuildingAssign,
    TaskAssign,
)

admin.site.register(Employee)

admin.site.register(User)
admin.site.register(Hierarchy)

admin.site.register(LeavesAvailable)
admin.site.register(LeavesTaken)
admin.site.register(Calendar)
admin.site.register(BiometricData)
admin.site.register(Project)
admin.site.register(Building)
admin.site.register(Task)
admin.site.register(ProjectAssign)
admin.site.register(BuildingAssign)
admin.site.register(TaskAssign)
