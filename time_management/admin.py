from django.contrib import admin

from .models import (
    User,
    Employee,
    Hierarchy,
    LeavesAvailable,
    LeavesTaken,
    Calendar,
    BiometricData,
    AreaOfWork,
    Discipline,
    Project,
    Building,
    Task,
    ProjectAssign,
    BuildingAssign,
    TaskAssign,
    TimeSheet,
    Attachment,
    CompOff,
    Variation,
    CompOffRequest,
)

admin.site.register(Employee)

admin.site.register(User)
admin.site.register(Hierarchy)

admin.site.register(LeavesAvailable)
admin.site.register(LeavesTaken)
admin.site.register(Calendar)
admin.site.register(BiometricData)
admin.site.register(Project)
admin.site.register(AreaOfWork)
admin.site.register(Discipline)
admin.site.register(Building)
admin.site.register(Task)
admin.site.register(ProjectAssign)
admin.site.register(BuildingAssign)
admin.site.register(TaskAssign)
admin.site.register(TimeSheet)
admin.site.register(Attachment)
admin.site.register(CompOff)
admin.site.register(CompOffRequest)
admin.site.register(Variation)
