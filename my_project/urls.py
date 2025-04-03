"""
URL configuration for my_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

### urls.py

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from time_management.models import (
    User,
    Employee,
    Hierarchy,
    LeavesAvailable,
    LeavesTaken,
    Calendar,
    BiometricData,
)
from time_management.employee.views import (
    employee_api,
    employee_view_api,
    mntl_view_api,
)
from time_management.user.views import user_api
from time_management.hierarchy.views import (
    hierarchy_api,
    manager_hierarchy,
    teamlead_hierarchy,
    org_hierarchy,
)
from time_management.leaves_available.views import leaves_available_api
from time_management.leaves_taken.views import leaves_taken_api
from time_management.calendar.views import calendar_api
from time_management.biometric.views import biometric_data_api
from time_management.project.views import (
    project_list_create,
    project_detail,
    project_assign_detail,
    project_assign_list_create,
)
from time_management.building.views import (
    building_list_create,
    building_detail,
    building_assign_detail,
    building_assign_list_create,
)
from time_management.task.views import (
    task_list_create,
    task_detail,
    task_assign_detail,
    task_assign_list_create,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("employees/", employee_api),
    path("employees/<str:employee_id>/", employee_api),
    path("employees-details/", employee_view_api),
    path("employees-details/<str:employee_id>/", employee_view_api),
    path("teamlead-and-managers/", mntl_view_api, name="managers-and-team-leads"),
    path("teamlead-and-managers/<str:employee_id>/", mntl_view_api),
    path("users/", user_api),
    path("users/<str:user_id>/", user_api),
    path("hierarchy/", hierarchy_api),
    path("hierarchy/<str:hierarchy_id>/", hierarchy_api),
    path("manager-hierarchy/", manager_hierarchy),
    path("manager-hierarchy/<str:manager_id>/", manager_hierarchy),
    path("teamlead-hierarchy/", teamlead_hierarchy),
    path("teamlead-hierarchy/<str:teamlead_id>/", teamlead_hierarchy),
    path("org-hierarchy/", org_hierarchy),
    path("org-hierarchy/<str:emp_id>/", org_hierarchy),
    path("leaves-available/", leaves_available_api),
    path("leaves-available/<str:leave_avail_id>/", leaves_available_api),
    path("leaves-taken/", leaves_taken_api),
    path("leaves-taken/<str:leave_taken_id>/", leaves_taken_api),
    path("calendar/", calendar_api),
    path("calendar/<str:calendar_id>/", calendar_api),
    path("biometric-data/", biometric_data_api),
    path("biometric-data/<str:biometric_id>/", biometric_data_api),
    path("projects/", project_list_create, name="project-list-create"),
    path("projects/<str:project_id>/", project_detail, name="project-detail"),
    path(
        "projects-assigned/",
        project_assign_list_create,
        name="project-assign-list-create",
    ),
    path(
        "projects-assigned/<str:project_assign_id>/",
        project_assign_detail,
        name="project-assign-detail",
    ),
    path("buildings/", building_list_create, name="building-list-create"),
    path("buildings/<str:building_id>/", building_detail, name="building-detail"),
    path(
        "buildings-assigned/",
        building_assign_list_create,
        name="building-assign-list-create",
    ),
    path(
        "buildings-assigned/<str:building_assign_id>/",
        building_assign_detail,
        name="building-assign-detail",
    ),
    path("tasks/", task_list_create, name="task-list-create"),
    path("tasks/<str:task_id>/", task_detail, name="task-detail"),
    path(
        "tasks-assigned/",
        task_assign_list_create,
        name="task-assign-list-create",
    ),
    path(
        "tasks-assigned/<str:task_assign_id>/",
        task_assign_detail,
        name="task-assign-detail",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
