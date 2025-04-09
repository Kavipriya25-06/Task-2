#############
### Timesheet Management System developed by Suriya Prakash Ammaiappan
### LinkedIn https://www.linkedin.com/in/suriyaprakashammaiappan/
#############

# ### models.py

from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, Group, Permission


# Employee Table
class Employee(models.Model):
    employee_id = models.CharField(max_length=50, primary_key=True, blank=True)
    employee_code = models.CharField(max_length=30, blank=True, null=True)
    employee_name = models.CharField(max_length=255, blank=True, null=True)
    fathers_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=40, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    doj = models.DateField(blank=True, null=True)
    contact_number = models.CharField(max_length=10, blank=True, null=True)
    personal_email = models.EmailField(unique=True, blank=True, null=True)
    aadhaar_number = models.CharField(max_length=12, blank=True, null=True)
    PAN = models.CharField(max_length=10, blank=True, null=True)
    UAN = models.CharField(max_length=12, blank=True, null=True)
    pf_number = models.CharField(max_length=20, blank=True, null=True)
    esi_number = models.CharField(max_length=20, blank=True, null=True)
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    passport_validity = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("resigned", "Resigned"),
        ],
        blank=True,
        null=True,
    )
    remarks = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    local_address = models.TextField(blank=True, null=True)

    # Employment details

    employment_type = models.CharField(max_length=50, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    qualification = models.CharField(max_length=100, blank=True, null=True)
    year_of_passing = models.IntegerField(default=0, blank=True, null=True)

    previous_company_name = models.CharField(max_length=255, null=True, blank=True)
    total_experience = models.IntegerField(default=0, blank=True, null=True)  # In years
    arris_experience = models.IntegerField(
        default=0, blank=True, null=True
    )  # Experience in current company

    total_experience = models.CharField(max_length=100, blank=True, null=True)
    experience_in_years = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    probation_confirmation_date = models.DateField(null=True, blank=True)

    employee_email = models.EmailField(unique=True, blank=True, null=True)
    reporting_manager = models.CharField(max_length=100, blank=True, null=True)
    resignation_date = models.DateField(null=True, blank=True)
    relieving_date = models.DateField(null=True, blank=True)

    # Bank Details
    account_number = models.CharField(max_length=20, null=True, blank=True)
    ifsc_code = models.CharField(max_length=11, null=True, blank=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True)

    # Emergency Details
    emergency_contact_name = models.CharField(max_length=255, blank=True, null=True)
    emergency_contact_number = models.CharField(max_length=15, blank=True, null=True)
    blood_group = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    updated_at = models.DateTimeField(auto_now=True)

    # profile_picture = models.ImageField(
    #     upload_to="profile_pics/", null=True, blank=True
    # )
    # attachments = models.FileField(
    #     upload_to="employee_attachments/", null=True, blank=True
    # )

    def save(self, *args, **kwargs):
        if not self.employee_id:
            with transaction.atomic():
                last = Employee.objects.select_for_update().aggregate(
                    models.Max("employee_id")
                )["employee_id__max"]
                if last:
                    last_num = int(last.split("_")[1])
                    self.employee_id = f"EMP_{last_num + 1:05d}"
                else:
                    self.employee_id = "EMP_00001"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.employee_id


class User(models.Model):
    user_id = models.CharField(max_length=50, primary_key=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(
        max_length=50,
        choices=[
            ("admin", "Admin"),
            ("hr", "HR"),
            ("teamlead", "Team Lead"),
            ("employee", "Employee"),
            ("manager", "Manager"),
        ],
    )
    employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.user_id:
            with transaction.atomic():
                last = User.objects.select_for_update().aggregate(
                    models.Max("user_id")
                )["user_id__max"]
                if last:
                    last_num = int(last.split("_")[1])
                    self.user_id = f"USR_{last_num + 1:05d}"
                else:
                    self.user_id = "USR_00001"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


# Hierarchy Table
class Hierarchy(models.Model):
    hierarchy_id = models.CharField(max_length=50, primary_key=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    designation = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    reporting_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
    )

    def save(self, *args, **kwargs):
        if not self.hierarchy_id:
            with transaction.atomic():
                last = Hierarchy.objects.select_for_update().aggregate(
                    models.Max("hierarchy_id")
                )["hierarchy_id__max"]
                if last:
                    last_num = int(last.split("_")[1])
                    self.hierarchy_id = f"HR_{last_num + 1:05d}"
                else:
                    self.hierarchy_id = "HR_00001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} reports to {self.reporting_to}"


# Leaves Available Table
class LeavesAvailable(models.Model):
    leave_avail_id = models.CharField(max_length=50, primary_key=True, blank=True)
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    sick_leave = models.IntegerField(default=0)
    casual_leave = models.IntegerField(default=0)
    comp_off = models.IntegerField(default=0)
    earned_leave = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.leave_avail_id:
            with transaction.atomic():
                last = LeavesAvailable.objects.select_for_update().aggregate(
                    models.Max("leave_avail_id")
                )["leave_avail_id__max"]
                if last:
                    last_num = int(last.split("_")[1])
                    self.leave_avail_id = f"LVAVL_{last_num + 1:05d}"
                else:
                    self.leave_avail_id = "LVAVL_00001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Leaves for {self.employee.employee_name}"


# Leaves Taken Table with Approval Workflow
class LeavesTaken(models.Model):
    leave_taken_id = models.CharField(max_length=50, primary_key=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.IntegerField()
    reason = models.TextField()
    resumption_date = models.DateField()
    attachment = models.FileField(upload_to="leave_attachments/", null=True, blank=True)

    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leaves",
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.leave_taken_id:
            with transaction.atomic():
                last = LeavesTaken.objects.select_for_update().aggregate(
                    models.Max("leave_taken_id")
                )["leave_taken_id__max"]
                if last:
                    last_num = int(last.split("_")[1])
                    self.leave_taken_id = f"LVTKN_{last_num + 1:05d}"
                else:
                    self.leave_taken_id = "LVTKN_00001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.leave_type} - {self.employee.employee_name}"


class Calendar(models.Model):
    calendar_id = models.CharField(max_length=50, primary_key=True, blank=True)
    date = models.DateField(unique=True)
    year = models.IntegerField()
    month = models.IntegerField()
    month_name = models.CharField(max_length=20)
    day = models.IntegerField()
    day_of_week = models.IntegerField()
    day_name = models.CharField(max_length=20)
    week_of_year = models.IntegerField()
    quarter = models.IntegerField()
    is_weekend = models.BooleanField(default=False)
    is_holiday = models.BooleanField(default=False)
    fiscal_year = models.IntegerField()
    notes = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.calendar_id:
            with transaction.atomic():
                last = Calendar.objects.select_for_update().aggregate(
                    models.Max("calendar_id")
                )["calendar_id__max"]
                if last:
                    last_num = int(last.split("_")[1])
                    self.calendar_id = f"CAL_{last_num + 1:05d}"
                else:
                    self.calendar_id = "CAL_00001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.day_name}"


class BiometricData(models.Model):
    biometric_id = models.CharField(max_length=50, primary_key=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    employee_code = models.CharField(max_length=50)
    employee_name = models.CharField(max_length=100)
    shift = models.CharField(max_length=50)
    date = models.DateField()
    in_time = models.TimeField()
    out_time = models.TimeField()
    work_duration = models.DecimalField(max_digits=5, decimal_places=2)
    ot = models.DecimalField("OT", max_digits=5, decimal_places=2)
    total_duration = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=50)
    remarks = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.biometric_id:
            with transaction.atomic():
                last = BiometricData.objects.select_for_update().aggregate(
                    models.Max("biometric_id")
                )["biometric_id__max"]
                if last:
                    last_num = int(last.split("_")[1])
                    self.biometric_id = f"BIO_{last_num + 1:09d}"
                else:
                    self.biometric_id = "BIO_000000001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_name} - {self.date}"


### Projects Table


class Project(models.Model):
    project_id = models.CharField(max_length=20, primary_key=True, blank=True)
    project_title = models.CharField(max_length=255)
    project_type = models.CharField(max_length=100)
    start_date = models.DateField()
    estimated_hours = models.DecimalField(max_digits=10, decimal_places=2)
    project_description = models.TextField(blank=True, null=True)
    area_of_work = models.CharField(max_length=255)
    project_code = models.CharField(max_length=100, unique=True)
    subdivision = models.CharField(max_length=100)
    discipline_code = models.CharField(max_length=100)
    discipline = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.project_id:
            with transaction.atomic():
                last = Project.objects.select_for_update().aggregate(
                    models.Max("project_id")
                )["project_id__max"]

                if last:
                    last_num = int(last.split("_")[1])
                    self.project_id = f"PROJ_{last_num + 1:05d}"
                else:
                    self.project_id = "PROJ_00001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project_title} ({self.project_id})"


# Helper function to generate auto ID


def generate_auto_id(model_class, prefix):
    last = model_class.objects.order_by("-id").first()
    if last and hasattr(last, model_class._meta.pk.name):
        last_num = int(getattr(last, model_class._meta.pk.name).split("_")[1])
        return f"{prefix}_{last_num + 1:05d}"
    return f"{prefix}_00001"


class Building(models.Model):
    building_id = models.CharField(max_length=50, primary_key=True, blank=True)
    building_title = models.CharField(max_length=200)
    building_description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True, blank=True, null=True)
    # created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    # updated_at = models.DateTimeField(auto_now=True)
    # created_by = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.building_id:
            self.building_id = generate_auto_id(Building, "BLD")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.building_title


class Task(models.Model):
    task_id = models.CharField(max_length=50, primary_key=True, blank=True)
    task_title = models.CharField(max_length=200)
    task_description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=50)
    attachments = models.FileField(
        upload_to="tasks/attachments/", blank=True, null=True
    )
    comments = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True, blank=True, null=True)
    # created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    # updated_at = models.DateTimeField(auto_now=True)
    # created_by = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.task_id:
            self.task_id = generate_auto_id(Task, "TASK")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.task_title


class ProjectAssign(models.Model):
    project_assign_id = models.CharField(max_length=50, primary_key=True, blank=True)
    project_hours = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(
        max_length=50,
        choices=[
            ("inprogress", "In Progress"),
            ("completed", "Completed"),
            ("pending", "Pending"),
        ],
        default="pending",
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)
    # created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    # updated_at = models.DateTimeField(auto_now=True)
    # created_by = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.project_assign_id:
            self.project_assign_id = generate_auto_id(ProjectAssign, "PRASS")
        super().save(*args, **kwargs)


class BuildingAssign(models.Model):
    building_assign_id = models.CharField(max_length=50, primary_key=True, blank=True)
    building_hours = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(
        max_length=50,
        choices=[
            ("inprogress", "In Progress"),
            ("completed", "Completed"),
            ("pending", "Pending"),
        ],
        default="pending",
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True)
    project_assign = models.ForeignKey(
        ProjectAssign, on_delete=models.SET_NULL, null=True
    )

    def save(self, *args, **kwargs):
        if not self.building_assign_id:
            self.building_assign_id = generate_auto_id(BuildingAssign, "BLASS")
        super().save(*args, **kwargs)


class TaskAssign(models.Model):
    task_assign_id = models.CharField(max_length=50, primary_key=True, blank=True)
    task_hours = models.DecimalField(max_digits=6, decimal_places=2)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("inprogress", "In Progress"),
            ("completed", "Completed"),
            ("pending", "Pending"),
        ],
        default="pending",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    building_assign = models.ForeignKey(
        BuildingAssign, on_delete=models.SET_NULL, null=True
    )

    def save(self, *args, **kwargs):
        if not self.task_assign_id:
            self.task_assign_id = generate_auto_id(TaskAssign, "TKASS")
        super().save(*args, **kwargs)


class TimeSheet(models.Model):
    timesheet_id = models.CharField(max_length=50, primary_key=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    task_assign = models.ForeignKey(TaskAssign, on_delete=models.SET_NULL, null=True)
    task_hours = models.DecimalField(max_digits=6, decimal_places=2)
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()

    def save(self, *args, **kwargs):
        if not self.timesheet_id:
            self.timesheet_id = generate_auto_id(TimeSheet, "TS")
        super().save(*args, **kwargs)


### Older tables

# # Projects Table
# class Project(models.Model):
#     project_id = models.AutoField(primary_key=True)
#     project_title = models.CharField(max_length=255)
#     project_type = models.CharField(max_length=100)
#     start_date = models.DateField()
#     estimated_hours = models.IntegerField()
#     project_description = models.TextField()

#     created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.project_title


# # Tasks Table
# class Task(models.Model):
#     task_id = models.AutoField(primary_key=True)
#     project = models.ForeignKey(Project, on_delete=models.CASCADE)
#     task_title = models.CharField(max_length=255)
#     task_hours = models.IntegerField()
#     start_date = models.DateField()
#     end_date = models.DateField()
#     task_description = models.TextField()
#     priority = models.CharField(
#         max_length=50,
#         choices=[
#             ("low", "Low"),
#             ("medium", "Medium"),
#             ("high", "High"),
#             ("urgent", "Urgent"),
#         ],
#     )
#     attachments = models.FileField(upload_to="task_attachments/", null=True, blank=True)
#     comments = models.TextField()

#     created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.task_title


# # Project Assignment Table
# class ProjectAssignment(models.Model):
#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
#     project = models.ForeignKey(Project, on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.employee.employee_name} assigned to {self.project.project_title}"


# # Task Assignment Table with Status Tracking
# class TaskAssignment(models.Model):
#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
#     task = models.ForeignKey(Task, on_delete=models.CASCADE)
#     status = models.CharField(
#         max_length=50,
#         choices=[
#             ("pending", "Pending"),
#             ("in_progress", "In Progress"),
#             ("completed", "Completed"),
#         ],
#         default="pending",
#     )
#     assigned_at = models.DateTimeField(auto_now_add=True)
#     completed_at = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return f"{self.employee.employee_name} assigned to {self.task.task_title}"
