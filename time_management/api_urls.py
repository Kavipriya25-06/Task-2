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

# from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

# from time_management.models import (
#     User,
#     Employee,
#     Hierarchy,
#     LeavesAvailable,
#     LeavesTaken,
#     Calendar,
#     BiometricData,
# )
# ---------- views imports (merged, unique names only) ----------
from time_management.attachments.views import (
    attachment_detail,
    attachment_list_create,
    attachments_by_employee,
    attachments_by_leavestaken,
    attachments_by_task,
    attachments_by_task_assign,
    attachments_by_project,
)
from time_management.employee.views import (
    employee_api,
    employee_view_api,
    mntl_view_api,
    active_mntl,
    emp_under_mngr_view,
    active_emp_under_mngr_view,
    active_emp_under_mngr_resign_date_view,
    additional_resource_view,
    unassigned_employee,
    employee_list_api,
    employee_all_details_api,
    get_last_employee,
)
from time_management.assignment.views import manager_tl_projects, tl_projects
from time_management.user.views import (
    user_api,
    user_details,
    login_details,
    send_reset_otp,
    reset_password,
)
from time_management.hierarchy.views import (
    hierarchy_api,
    manager_hierarchy,
    teamlead_hierarchy,
    org_hierarchy,
    get_emp_all,
    get_hierarchy_by_employee,
    teamleads_under_manager,
    department_chart,
    manager_chart,
)
from time_management.leaves_available.views import (
    leaves_available_api,
    comp_off_api,
    leaves_available_with_lop,
)
from time_management.leaves_taken.views import (
    leaves_taken_api,
    org_leaves,
    leave_request_api,
)
from time_management.calendar.views import calendar_api
from time_management.biometric.views import (
    biometric_view_api,
    biometric_data_api,
    attendance,
    weekly_attendance,
    weekly_attendance_track,
    attendance_track,
    attendance_admin,
    biometric_daily,
    biometric_daily_task,
    biometric_manager_daily_task,
    biometric_weekly_task,
    bulk_biometric_upload,
    biometric_weekly_track,
)
from time_management.client.views import (
    client_api,
    client_poc_api,
    client_poc_by_client_api,
    client_and_poc,
)
from time_management.leaveday.views import (
    leave_day_api,
    leave_ledger_ytd,
    opening_plus_monthly_availed,
    opening_plus_monthly_availed_all,
)
from time_management.compoff.views import (
    compoff_request_api,
    compoff_view_api,
    compoff_manager_view_api,
    comp_off_expiry_api,
)
from time_management.project.views import (
    project_list_create,
    project_detail,
    project_assign_detail,
    project_assign_list_create,
    project_assign_update,
    project_and_assign,
    areaofwork_api,
    discipline_api,
    create_full_project_flow,
    project_screen,
    full_project_view,
    project_creator,
    export_report,
    project_assigned_employee,
)
from time_management.reports.views import (
    hours_project_view,
    get_last_project,
    get_last_building,
    get_last_task,
    year_leaves,
    weekly_hours_project,
    monthly_hours_project,
    yearly_hours_project,
    employee_report_week,
    leaves_available_report,
    active_leaves_available_report,
    employee_lop_view,
    department_weekly_hours_project,
    weekly_employees,
    attrition_report,
    monthly_attendance_summary,
)
from time_management.variations.views import variation_api
from time_management.building.views import (
    building_list_create,
    building_detail,
    building_assign_detail,
    building_assign_list_create,
    building_and_assign,
    building_and_project,
    full_building_view,
    building_assign_update,
    create_building_with_assignment,
    test_post,
    building_assign_create,
    building_by_employee,
    default_building,
    other_building,
)
from time_management.task.views import (
    task_list_create,
    task_detail,
    task_assign_detail,
    task_assign_list_create,
    task_and_assign,
    task_and_assign_test,
    task_building,
    task_by_employee,
    default_task_by_employee,
    default_tasks,
    other_tasks,
    upsert_tasks_assigned,
)
from time_management.time_sheet.views import (
    timesheet_data_api,
    timesheet_under_manager,
    manager_weekly_timesheet,
    manager_daily_timesheet,
    employee_weekly_timesheet,
    employee_daily_timesheet,
    total_logged_hours,
)

from time_management.modifications.views import modifications_api
from time_management.designation.views import designation_api
from time_management.department.views import department_api
from time_management.assets.views import assets_api
from time_management.dependant.views import dependant_api
from time_management.education.views import education_api
from time_management.workexperience.views import work_experience_api
from time_management.languagesknown.views import languages_known_api
from time_management.employee_attachment.views import employee_attachment_api
from time_management.company_policy.views import company_policy_api
from time_management.salarybreakdown.views import salary_breakdown_api

from time_management.services.leave_ledger import get_monthly_leave_report

from time_management.views import MyTokenObtainPairView, run_biometric_sync
from rest_framework_simplejwt.views import TokenRefreshView

# ---------- urlpatterns (single, deduplicated list) ----------
urlpatterns = [
    # path("admin/", admin.site.urls),
    # Employees & related
    path("sync-biometric/", run_biometric_sync, name="sync-biometric"),
    path("employees/", employee_api),
    path("employees/<str:employee_id>/", employee_api),
    path("employees-details/", employee_view_api),
    path("employees-details/<str:employee_id>/", employee_view_api),
    path("employees-list/", employee_list_api),
    path("employees-list/<str:employee_id>/", employee_list_api),
    path("employees-all-details/", employee_all_details_api),
    path("employees-all-details/<str:employee_id>/", employee_all_details_api),
    path("unassigned-employees/", unassigned_employee),
    path("last-employee/", get_last_employee, name="last-employee"),
    # Employee helper endpoints
    path("emp-details/", emp_under_mngr_view),
    path("emp-details/<str:employee_id>/", emp_under_mngr_view),
    path("emp-details-resg/", active_emp_under_mngr_resign_date_view),
    path("emp-details-resg/<str:employee_id>/", active_emp_under_mngr_resign_date_view),
    path("active-emp-details/", active_emp_under_mngr_view),
    path("active-emp-details/<str:employee_id>/", active_emp_under_mngr_view),
    path("additional-resource/", additional_resource_view),
    path("additional-resource/<str:employee_id>/", additional_resource_view),
    # Managers & team leads
    path("teamlead-and-managers/", mntl_view_api, name="managers-and-team-leads"),
    path("teamlead-and-managers/<str:employee_id>/", mntl_view_api),
    path("active-teamlead-and-managers/", active_mntl, name="managers-and-team-leads"),
    path("active-teamlead-and-managers/<str:employee_id>/", active_mntl),
    path("teamlead-managers-projects/", manager_tl_projects),
    path("teamlead-managers-projects/<str:employee_id>/", manager_tl_projects),
    path("teamlead_projects/", tl_projects),
    path("teamlead_projects/<str:employee_id>/", tl_projects),
    # Auth / users
    path("login-details/", login_details),
    path("login-details/<str:email>/", login_details),
    path("login-details/<str:email>/<str:password>/", login_details),
    path("users/", user_api),
    path("users/<str:user_id>/", user_api),
    path("user-details/", user_details),
    path("user-details/<str:user_id>/", user_details),
    path("send-otp/", send_reset_otp),
    path("reset-password/", reset_password),
    # Hierarchy / org chart
    path("hierarchy/", hierarchy_api),
    path("hierarchy/<str:hierarchy_id>/", hierarchy_api),
    path("hierarchy/by_employee/", get_hierarchy_by_employee),
    path("hierarchy/by_employee/<str:employee_id>/", get_hierarchy_by_employee),
    path("manager-hierarchy/", manager_hierarchy),
    path("manager-hierarchy/<str:manager_id>/", manager_hierarchy),
    path("all-employee-hierarchy/", get_emp_all),
    path("all-employee-hierarchy/<str:manager_id>/", get_emp_all),
    path("teamlead-hierarchy/", teamlead_hierarchy),
    path("teamlead-hierarchy/<str:teamlead_id>/", teamlead_hierarchy),
    path("org-hierarchy/", org_hierarchy),
    path("org-hierarchy/<str:emp_id>/", org_hierarchy),
    path("orgchart/department/", department_chart),
    path("orgchart/manager/", manager_chart),
    path("hierarchy/by_employee/<str:employee_id>/", get_hierarchy_by_employee),
    # Leaves & comp-off
    path("leaves-available/", leaves_available_api),
    path("leaves-available/<str:leave_avail_id>/", leaves_available_api),
    path("leaves-available/by_employee/<str:employee_id>/", leaves_available_api),
    path("leaves-available-lop/<str:employee_id>/", leaves_available_with_lop),
    path("comp-off/", comp_off_api),
    path("comp-off/<int:id>/", comp_off_api),
    path("comp-off-expiry/", comp_off_expiry_api),
    path("comp-off-expiry/<int:id>/", comp_off_expiry_api),
    path("comp-off-request/", compoff_request_api),
    path("comp-off-request/<str:compoff_request_id>/", compoff_request_api),
    path("comp-off-view/", compoff_view_api),
    path("comp-off-view/request/<str:compoff_request_id>/", compoff_view_api),
    path("comp-off-view/employee/<str:employee_id>/", compoff_view_api),
    path("comp-off-manager-view/", compoff_manager_view_api),
    path(
        "comp-off-manager-view/request/<str:compoff_request_id>/",
        compoff_manager_view_api,
    ),
    path("comp-off-manager-view/manager/<str:manager_id>/", compoff_manager_view_api),
    # Leaves taken / requests / reports
    path("leaves-taken/", leaves_taken_api),
    path("leaves-taken/<str:leave_taken_id>/", leaves_taken_api),
    path("leaves-taken/by_employee/<str:employee_id>/", leaves_taken_api),
    path("leave-day/", leave_day_api),
    path("leave-day/<int:id>/", leave_day_api),
    path("leave-day/by_employee/<str:employee_id>/", leave_day_api),
    path("leave-ledger/<int:year>/", leave_ledger_ytd, name="leave-ledger-ytd"),
    path(
        "leave/opening-monthly/<str:employee_id>/<int:year>/",
        opening_plus_monthly_availed,
        name="leave-opening-plus-monthly",
    ),
    path(
        "leave/opening-monthly-all/<int:year>/",
        opening_plus_monthly_availed_all,
        name="leave-opening-monthly-all",
    ),
    path("yearly-leaves/", year_leaves),
    path("leaves-available-report/", leaves_available_report),
    path("active-leaves-available-report/", active_leaves_available_report),
    path("employee-lop/", employee_lop_view),
    path("attrition-report/", attrition_report),
    path("monthly-attendance-report/", monthly_attendance_summary),
    path("leave-request/", leave_request_api),
    path("leave-request/<str:manager_id>/", leave_request_api),
    # Calendar
    path("calendar/", calendar_api),
    path("calendar/<str:calendar_id>/", calendar_api),
    # Biometric / attendance
    path("biometric-view/", biometric_view_api),
    path("biometric-view/<str:biometric_id>/", biometric_view_api),
    path("biometric-data/", biometric_data_api),
    path("biometric-data/<str:biometric_id>/", biometric_data_api),
    path("biometric-data/by_employee/<str:employee_id>/", biometric_data_api),
    path("biometric-daily/<str:employee_id>/", biometric_daily),
    path("biometric-daily-task/<str:employee_id>/", biometric_daily_task),
    path("biometric-weekly-task/<str:employee_id>/", biometric_weekly_task),
    path("biometric-weekly-track/<str:employee_id>/", biometric_weekly_track),
    path(
        "biometric-manager-daily-task/<str:manager_id>/", biometric_manager_daily_task
    ),
    path("attendance/", attendance),
    path("attendance/<str:employee_id>/", attendance),
    path("attendance-admin/", attendance_admin),
    path("attendance-admin/<str:employee_id>/", attendance_admin),
    path("attendance-upload/", bulk_biometric_upload),
    path("weekly-attendance/", weekly_attendance),
    path("weekly-attendance/<str:employee_id>/", weekly_attendance),
    path("weekly-attendance-track/", attendance_track),
    path("weekly-attendance-track/<str:employee_id>/", attendance_track),
    # Projects / assignments / reports
    path("client/", client_api),
    path("client/<int:id>/", client_api),
    path("client-poc/", client_poc_api),
    path("client-poc/<int:id>/", client_poc_api),
    path("client-poc-by-client/<int:client_id>/", client_poc_by_client_api),
    path("client-and-poc/", client_and_poc),
    path("projects/", project_list_create, name="project-list-create"),
    path("projects/create/", create_full_project_flow, name="project-create-all"),
    path("projects/<str:project_id>/", project_detail, name="project-detail"),
    path("last-project/", get_last_project, name="last-project"),
    path("last-building/<str:project_id>/", get_last_building, name="last-building"),
    path("last-task/", get_last_task, name="last-task"),
    path("project-hours/", hours_project_view, name="project-hours"),
    path("project-hours/<str:project_id>/", hours_project_view, name="project-hours"),
    path("weekly-project-hours/", weekly_hours_project, name="project-hours"),
    path(
        "weekly-project-hours/<str:project_id>/",
        weekly_hours_project,
        name="project-hours",
    ),
    path("monthly-project-hours/", monthly_hours_project, name="project-hours"),
    path(
        "monthly-project-hours/<str:project_id>/",
        monthly_hours_project,
        name="project-hours",
    ),
    path("yearly-project-hours/", yearly_hours_project, name="project-hours"),
    path(
        "yearly-project-hours/<str:project_id>/",
        yearly_hours_project,
        name="project-hours",
    ),
    path(
        "department-project-hours/",
        department_weekly_hours_project,
        name="project-hours",
    ),
    path(
        "department-project-hours/<str:department>/",
        department_weekly_hours_project,
        name="project-hours",
    ),
    path("weekly-employees/", weekly_employees, name="project-hours"),
    path("weekly-employees/<str:department>/", weekly_employees, name="project-hours"),
    path("variation/", variation_api, name="variation-detail"),
    path("variation/<int:id>/", variation_api, name="variation-detail"),
    path("projects-screen/", full_project_view, name="project-detail"),
    path("projects-screen/<str:project_id>/", full_project_view, name="project-detail"),
    path("buildings-screen/", full_building_view, name="project-detail"),
    path(
        "buildings-screen/<str:building_assign_id>/",
        full_building_view,
        name="project-detail",
    ),
    path(
        "projects-assigned/",
        project_assign_list_create,
        name="project-assign-list-create",
    ),
    path(
        "projects-assign-update/<str:project_assign_id>/",
        project_assign_update,
        name="project-assign-detail",
    ),
    path(
        "projects-assigned/<str:project_assign_id>/",
        project_assign_detail,
        name="project-assign-detail",
    ),
    path(
        "projects-assigned-employee/",
        project_assigned_employee,
        name="project-assigned-employee",
    ),
    path(
        "projects-assigned-employee/<str:project_assign_id>/",
        project_assigned_employee,
        name="project-assigned-employee",
    ),
    path(
        "projects-and-assigned/", project_and_assign, name="project-assign-list-create"
    ),
    path(
        "projects-and-assigned/<str:project_assign_id>/",
        project_and_assign,
        name="project-assign-detail",
    ),
    path("project-creator/", project_creator),
    path("project-creator/<str:employee_id>/", project_creator),
    path("export-report/", export_report),
    path("area-of-work/", areaofwork_api, name="Area-of-work"),
    path("area-of-work/<int:id>/", areaofwork_api, name="Area-of-work"),
    path("discipline/", discipline_api, name="Discipline"),
    path("discipline/<int:id>/", discipline_api, name="Discipline"),
    # Buildings
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
    path(
        "buildings-assign-update/",
        building_assign_update,
        name="building-assign-detail",
    ),
    path("buildings-create/", building_assign_create, name="building-create-all"),
    path("test-post/", test_post, name="test-create-all"),
    path("buildings-and-assigned/", building_and_assign, name="building-and-assign"),
    path(
        "buildings-and-assigned/<str:building_assign_id>/",
        building_and_assign,
        name="building-and-assign",
    ),
    path("buildings-and-projects/", building_and_project, name="building-and-project"),
    path(
        "buildings-and-projects/<str:building_assign_id>/",
        building_and_project,
        name="building-and-project",
    ),
    path("buildings-by-employee/", building_by_employee, name="Tasks-and-buildings"),
    path(
        "buildings-by-employee/<str:employee_id>/",
        building_by_employee,
        name="tasks-and-buildings",
    ),
    path("default-buildings/", default_building, name="default-buildings"),
    path("other-buildings/", other_building, name="other-buildings"),
    # Tasks
    path("tasks/", task_list_create, name="task-list-create"),
    path("tasks/<str:task_id>/", task_detail, name="task-detail"),
    path("tasks-assigned/", task_assign_list_create, name="task-assign-list-create"),
    path(
        "tasks-assigned/<str:task_assign_id>/",
        task_assign_detail,
        name="task-assign-detail",
    ),
    path("tasks-and-assigned/", task_and_assign, name="task-assign-list-create"),
    path(
        "tasks-and-assigned/<str:task_assign_id>/",
        task_and_assign,
        name="task-assign-detail",
    ),
    path("tasks-building/", task_building, name="Tasks-and-buildings"),
    path(
        "tasks-building/<str:task_assign_id>/",
        task_building,
        name="tasks-and-buildings",
    ),
    path("tasks-by-employee/", task_by_employee, name="Tasks-and-buildings"),
    path(
        "tasks-by-employee/<str:employee_id>/",
        task_by_employee,
        name="tasks-and-buildings",
    ),
    path("default-tasks/", default_tasks, name="Tasks-and-buildings"),
    path("default-tasks/<str:employee_id>/", default_tasks, name="tasks-and-buildings"),
    path("other-tasks/", other_tasks, name="Tasks-and-buildings"),
    path(
        "default-tasks-by-employee/",
        default_task_by_employee,
        name="Tasks-and-buildings",
    ),
    path("upsert-tasks/", upsert_tasks_assigned, name="Tasks-and-buildings"),
    # Timesheet
    path("timesheet/", timesheet_data_api, name="timesheet"),
    path("timesheet/<str:timesheet_id>/", timesheet_data_api, name="timesheet"),
    path("timesheet-manager/", timesheet_under_manager, name="timesheet"),
    path(
        "timesheet-manager/<str:employee_id>/",
        timesheet_under_manager,
        name="timesheet",
    ),
    path("timesheet-manager-weekly/", manager_weekly_timesheet, name="timesheet"),
    path(
        "timesheet-manager-weekly/<str:employee_id>/",
        manager_weekly_timesheet,
        name="timesheet",
    ),
    path("timesheet-manager-daily/", manager_daily_timesheet, name="timesheet"),
    path(
        "timesheet-manager-daily/<str:employee_id>/",
        manager_daily_timesheet,
        name="timesheet",
    ),
    path("timesheet-employee-weekly/", employee_weekly_timesheet, name="timesheet"),
    path(
        "timesheet-employee-weekly/<str:employee_id>/",
        employee_weekly_timesheet,
        name="timesheet",
    ),
    path("timesheet-employee-daily/", employee_daily_timesheet, name="timesheet"),
    path(
        "timesheet-employee-daily/<str:employee_id>/",
        employee_daily_timesheet,
        name="timesheet",
    ),
    path("employee-report-week/", employee_report_week, name="timesheet"),
    path(
        "employee-report-week/<str:employee_id>/",
        employee_report_week,
        name="timesheet",
    ),
    path("total-hours/project/<str:project_id>/", total_logged_hours, name="timesheet"),
    path(
        "total-hours/building/<str:building_id>/", total_logged_hours, name="timesheet"
    ),
    path("total-hours/task/<str:task_id>/", total_logged_hours, name="timesheet"),
    # Attachments
    path("attachments/", attachment_list_create, name="attachment_list_create"),
    path("attachments/<int:pk>/", attachment_detail, name="attachment_detail"),
    path(
        "attachments/task/<str:task_id>/",
        attachments_by_task,
        name="attachments_by_task",
    ),
    path(
        "attachments/task-assign/<str:task_assign_id>/",
        attachments_by_task_assign,
        name="attachments_by_task_assign",
    ),
    path(
        "attachments/employee/<str:employee_id>/",
        attachments_by_employee,
        name="attachments_by_employee",
    ),
    path(
        "attachments/leavestaken/<str:leave_taken_id>/",
        attachments_by_leavestaken,
        name="attachments_by_leavestaken",
    ),
    path(
        "attachments/project/<str:project_id>/",
        attachments_by_project,
        name="attachments_by_project",
    ),
    # Misc: modifications, designation, assets, dependant, education, work-experience, languages-known, employee-attachment, company-policy
    path("modifications/", modifications_api),
    path("modifications/<int:id>/", modifications_api),
    path("designation/", designation_api),
    path("designation/<int:id>/", designation_api),
    path("department/", department_api),
    path("department/<int:id>/", department_api),
    path("assets/", assets_api),
    path("assets/<int:id>/", assets_api),
    path("dependant/", dependant_api),
    path("dependant/<int:id>/", dependant_api),
    path("education/", education_api),
    path("education/<int:id>/", education_api),
    path("work-experience/", work_experience_api),
    path("work-experience/<int:id>/", work_experience_api),
    path("languages-known/", languages_known_api),
    path("languages-known/<int:id>/", languages_known_api),
    path("employee-attachment/", employee_attachment_api),
    path("employee-attachment/<int:id>/", employee_attachment_api),
    path("company-policy/", company_policy_api),
    path("company-policy/<int:id>/", company_policy_api),
    path("salary/", salary_breakdown_api),
    path("salary/<int:id>/", salary_breakdown_api),
    # JWT tokens (commented out in original)
    # path("api/token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
