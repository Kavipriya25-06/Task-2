#############
### Timesheet Management System developed by Suriya Prakash Ammaiappan
### LinkedIn https://www.linkedin.com/in/suriyaprakashammaiappan/
#############

# ### models.py

from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, Group, Permission
from datetime import date
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
import uuid


# Employee Table
class Employee(models.Model):
    employee_id = models.CharField(max_length=50, primary_key=True, blank=True)
    employee_code = models.CharField(max_length=30, unique=True, blank=True, null=True)
    employee_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    fathers_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=40, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    age = models.IntegerField(default=0, blank=True, null=True)
    doj = models.DateField(blank=True, null=True)
    contact_number = models.CharField(max_length=10, blank=True, null=True)
    identification_marks = models.TextField(blank=True, null=True)
    wedding_date = models.DateField(blank=True, null=True)
    personal_email = models.EmailField(unique=True, blank=True, null=True)
    aadhaar_number = models.CharField(max_length=20, blank=True, null=True)
    PAN = models.CharField(max_length=10, blank=True, null=True)
    UAN = models.CharField(max_length=12, blank=True, null=True)
    pf_number = models.CharField(max_length=22, blank=True, null=True)
    esi_number = models.CharField(max_length=20, blank=True, null=True)
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    passport_validity = models.DateField(null=True, blank=True)
    onboarding_status = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
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
    location = models.CharField(max_length=100, blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    local_address = models.TextField(blank=True, null=True)

    # Employment details

    employment_type = models.CharField(
        max_length=50,
        choices=[
            ("Fulltime", "Full-Time"),
            ("Probation", "Probation"),
            ("Internship", "Internship"),
            ("Contract", "Contract"),
        ],
        blank=True,
        null=True,
    )
    designation = models.CharField(max_length=100, blank=True, null=True)
    source_of_hire = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    qualification = models.CharField(max_length=100, blank=True, null=True)
    year_of_passing = models.IntegerField(default=0, blank=True, null=True)

    previous_company_name = models.CharField(max_length=255, null=True, blank=True)
    previous_experience = models.IntegerField(
        default=0, blank=True, null=True
    )  # In months
    aero360_experience = models.IntegerField(
        default=0, blank=True, null=True
    )  # Experience in current company in months

    total_experience = models.IntegerField(
        default=0, blank=True, null=True
    )  # in months
    experience_in_years = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    probation_confirmation_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    employee_email = models.EmailField(unique=True, blank=True, null=True)
    reporting_manager = models.CharField(max_length=100, blank=True, null=True)
    second_reporting_manager = models.CharField(max_length=100, blank=True, null=True)
    resignation_date = models.DateField(null=True, blank=True)
    relieving_date = models.DateField(null=True, blank=True)
    seating_location = models.CharField(max_length=100, blank=True, null=True)
    work_phone = models.CharField(max_length=100, blank=True, null=True)
    extension = models.CharField(max_length=100, blank=True, null=True)

    # Bank Details
    account_number = models.CharField(max_length=20, null=True, blank=True)
    ifsc_code = models.CharField(max_length=11, null=True, blank=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    bank_branch_name = models.CharField(max_length=100, null=True, blank=True)
    bank_address = models.CharField(max_length=1000, null=True, blank=True)

    # Emergency Details
    emergency_contact_name = models.CharField(max_length=255, blank=True, null=True)
    emergency_contact_relationship = models.CharField(
        max_length=255, blank=True, null=True
    )
    emergency_contact_number = models.CharField(max_length=15, blank=True, null=True)
    blood_group = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    updated_at = models.DateTimeField(auto_now=True)

    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )
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
        # --------- ARRIS EXPERIENCE AUTO-CALCULATION ---------

        if self.doj and isinstance(self.doj, date):
            today = date.today()
            delta = (today.year - self.doj.year) * 12 + (today.month - self.doj.month)
            if delta < 0:
                delta = 0  # Future DOJ safety
            self.arris_experience = delta
        else:
            self.arris_experience = 0

        # --------- TOTAL EXPERIENCE AUTO-CALCULATION ---------
        self.total_experience = (self.arris_experience or 0) + (
            self.previous_experience or 0
        )

        # --------- EXPERIENCE IN YEARS (for display) ---------
        self.experience_in_years = (
            round(self.total_experience / 12, 2) if self.total_experience else 0
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.employee_id


class Modifications(models.Model):

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, blank=True, null=True
    )

    modified_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="modified",
    )

    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee} updated by {self.modified_by or 0} at {self.created_at or 0}"


### roles table


class Roles(models.Model):
    role = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.role


class Designation(models.Model):
    designation = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.designation


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
        default="employee",
    )
    # role = models.ManyToManyField(Roles, blank=True)
    employee_id = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
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

    def save(self, *args, **kwargs):
        is_new = not self.user_id
        previous = None
        changed_fields = []

        if not is_new:
            try:
                previous = User.objects.get(user_id=self.user_id)
            except User.DoesNotExist:
                pass

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

        # Password hashing
        if self.password and not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)

        super().save(*args, **kwargs)

        # ---- Send Email if it's an update ----
        if previous is not None:
            if previous.password != self.password:
                changed_fields.append("password")
            if previous.status != self.status:
                changed_fields.append("status")
            if previous.role != self.role:
                changed_fields.append("role")

            if changed_fields:
                subject = "Your user account has been updated"
                changes = ", ".join(changed_fields)
                message = (
                    f"Dear {self.employee_id.employee_name},\n\n"
                    f"The following fields in your user account have been changed: {changes}.\n\n"
                    "If you did not request these changes, please contact admin support immediately.\n\n"
                    "Regards,\nAdmin Team"
                )
                email = EmailMessage(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [self.email],  # self.email when in production
                    cc=[settings.ADMIN_EMAIL],  # CC admin
                )
                try:
                    email.send()
                    # return
                except Exception as e:
                    print(f"[ERROR] Email not sent: {e}")

    def __str__(self):
        return (
            f"{self.employee_id.employee_name or 0} - {self.email} - {self.employee_id}"
        )


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return (timezone.now() - self.created_at).seconds > 600  # 10 minutes

    def is_throttle_limited(self):
        return (timezone.now() - self.created_at).seconds < 60  # less than 60s ago


class Assets(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    model = models.CharField(max_length=50, blank=True)
    type = models.CharField(max_length=50, blank=True)
    serialnumber = models.CharField(max_length=50, blank=True)
    given_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.employee} owns {self.type}"


class Dependant(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True, null=True)
    relationship = models.CharField(max_length=50, blank=True, null=True)
    # relevance = models.BooleanField(default=False, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    age = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return f"{self.employee} dependant {self.name}"


class Education(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    institution_name = models.CharField(max_length=50, blank=True, null=True)
    degree = models.CharField(max_length=50, blank=True, null=True)
    specialization = models.CharField(max_length=50, blank=True, null=True)
    # relevance = models.BooleanField(default=False, blank=True, null=True)
    # start_date = models.DateField(blank=True, null=True)
    date_of_completion = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.employee} studied at {self.institution_name}"


class WorkExperience(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=50, blank=True, null=True)
    company_role = models.CharField(max_length=50, blank=True, null=True)
    relevance = models.BooleanField(default=False, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.employee} worked at {self.company_name}"


class LanguagesKnown(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    language = models.CharField(max_length=50, blank=True, null=True)
    read = models.CharField(
        max_length=50,
        choices=[
            ("Native", "Native"),
            ("Fluent", "Fluent"),
            ("Proficient", "Proficient"),
            ("Basic", "Basic"),
            ("Conversational", "Conversational"),
        ],
        blank=True,
        null=True,
    )
    write = models.CharField(
        max_length=50,
        choices=[
            ("Native", "Native"),
            ("Fluent", "Fluent"),
            ("Proficient", "Proficient"),
            ("Basic", "Basic"),
            ("Conversational", "Conversational"),
        ],
        blank=True,
        null=True,
    )
    speak = models.CharField(
        max_length=50,
        choices=[
            ("Native", "Native"),
            ("Fluent", "Fluent"),
            ("Proficient", "Proficient"),
            ("Basic", "Basic"),
            ("Conversational", "Conversational"),
        ],
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.employee} knows {self.language}"


# Hierarchy Table
class Hierarchy(models.Model):
    hierarchy_id = models.CharField(max_length=50, primary_key=True, blank=True)
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, blank=True, null=True
    )
    designation = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    reporting_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
    )
    second_reporting_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="second_reports",
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

        # Sync designation and department from the employee model
        if self.employee:
            self.designation = self.employee.designation
            self.department = self.employee.department

            # Auto-set reporting_to based on employee.reporting_manager field
            if self.employee.reporting_manager:
                try:
                    manager = (
                        Employee.objects.filter(
                            employee_id=self.employee.reporting_manager
                        ).first()
                        or Employee.objects.filter(
                            employee_code=self.employee.reporting_manager
                        ).first()
                    )
                    self.reporting_to = manager
                except Employee.DoesNotExist:
                    self.reporting_to = None  # fallback if name not found

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} reports to {self.reporting_to}"


class CompOff(models.Model):

    leave_type = models.CharField(
        max_length=20,
        choices=[
            ("full_day", "Full Day"),
            ("half_day", "Half Day"),
        ],
        unique=True,
    )
    min_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Minimum hours required to avoid this leave type",
    )
    max_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Maximum hours after which this leave type does not apply",
    )

    def __str__(self):
        return f"{self.leave_type}: {self.min_hours} - {self.max_hours} hrs"


# Leaves Taken Table with Approval Workflow
class CompOffRequest(models.Model):
    compoff_request_id = models.CharField(max_length=50, primary_key=True, blank=True)
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, blank=True, null=True
    )
    # leave_type = models.CharField(max_length=100)
    # start_date = models.DateField()
    date = models.DateField()
    duration = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True, default=0
    )
    reason = models.TextField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)

    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_compoff",
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ("eligible", "Eligible"),
            ("expired", "Expired"),
            ("applied", "Applied"),
            ("availed", "Availed"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.compoff_request_id:
            with transaction.atomic():
                last = CompOffRequest.objects.select_for_update().aggregate(
                    models.Max("compoff_request_id")
                )["compoff_request_id__max"]
                if last:
                    last_num = int(last.split("_")[1])
                    self.compoff_request_id = f"CR_{last_num + 1:05d}"
                else:
                    self.compoff_request_id = "CR_00001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.employee.employee_name}"


# Leaves Available Table
class LeavesAvailable(models.Model):
    leave_avail_id = models.CharField(max_length=50, primary_key=True, blank=True)
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, blank=True, null=True
    )
    sick_leave = models.DecimalField(
        max_digits=6, decimal_places=1, blank=True, null=True, default=0
    )
    casual_leave = models.DecimalField(
        max_digits=6, decimal_places=1, blank=True, null=True, default=0
    )
    comp_off = models.DecimalField(
        max_digits=6, decimal_places=1, blank=True, null=True, default=0
    )
    earned_leave = models.DecimalField(
        max_digits=6, decimal_places=1, blank=True, null=True, default=0
    )

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
    employee = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, blank=True, null=True
    )
    leave_type = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.DecimalField(
        max_digits=6, decimal_places=1, blank=True, null=True, default=0
    )
    reason = models.TextField(blank=True, null=True)
    resumption_date = models.DateField(
        null=True,
        blank=True,
    )
    # attachment = models.FileField(upload_to="leave_attachments/", null=True, blank=True)

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
    comp_off_date = models.DateField(
        null=True,
        blank=True,
    )

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
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, blank=True, null=True
    )
    employee_code = models.CharField(max_length=50)
    employee_name = models.CharField(max_length=100)
    shift = models.CharField(max_length=50, blank=True, null=True)
    group_id = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField()
    in_time = models.TimeField()
    out_time = models.TimeField(blank=True, null=True)
    work_duration = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ot = models.DecimalField("OT", max_digits=5, decimal_places=2, default=0)
    total_duration = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=50, default="Present")
    remarks = models.TextField(blank=True, null=True)
    modified_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="manager",
    )
    modified_on = models.DateTimeField(auto_now=True)

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


### Area of work table static


class AreaOfWork(models.Model):
    area_name = models.CharField(
        max_length=100, unique=True, primary_key=True, default="qc"
    )
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Discipline(models.Model):
    discipline_code = models.IntegerField(unique=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


### Projects Table


class Project(models.Model):
    project_id = models.CharField(max_length=20, primary_key=True, blank=True)
    project_title = models.CharField(max_length=255, blank=True, null=True)
    project_type = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_status = models.BooleanField(default=False, blank=True, null=True)
    estimated_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    variation_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    consumed_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    project_description = models.TextField(blank=True, null=True)
    # area_of_work = models.ManyToManyField(AreaOfWork, blank=True)
    project_code = models.CharField(max_length=100, unique=True)
    # subdivision = models.CharField(max_length=100)
    discipline_code = models.CharField(max_length=100)
    discipline = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, blank=True, null=True
    )

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

        # Recalculate total hours
        self.total_hours = (self.estimated_hours or 0) + (self.variation_hours or 0)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project_title} ({self.project_id})"


# Helper function to generate auto ID


def generate_auto_id(model_class, prefix):
    pk_name = model_class._meta.pk.name
    last = model_class.objects.order_by(f"-{pk_name}").first()
    if last and hasattr(last, model_class._meta.pk.name):
        last_num = int(getattr(last, model_class._meta.pk.name).split("_")[1])
        return f"{prefix}_{last_num + 1:05d}"
    return f"{prefix}_00001"


class Building(models.Model):
    building_id = models.CharField(max_length=50, primary_key=True, blank=True)
    building_title = models.CharField(max_length=200)
    building_description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True, blank=True, null=True)
    building_code = models.CharField(max_length=21, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_status = models.BooleanField(default=False, blank=True, null=True)
    # created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    # updated_at = models.DateTimeField(auto_now=True)
    # created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL)

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
    priority = models.CharField(max_length=50, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_status = models.BooleanField(default=False, blank=True, null=True)
    # attachments = models.FileField(
    #     upload_to="tasks/attachments/", blank=True, null=True
    # )
    comments = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True, blank=True, null=True)
    task_code = models.CharField(max_length=21, unique=True)
    # created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    # updated_at = models.DateTimeField(auto_now=True)
    # created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL)

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
    employee = models.ManyToManyField(Employee, blank=True)
    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, null=True, blank=True
    )
    # created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    # updated_at = models.DateTimeField(auto_now=True)
    # created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL)

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
    employee = models.ManyToManyField(Employee, blank=True)
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, null=True, blank=True
    )
    project_assign = models.ForeignKey(
        ProjectAssign, on_delete=models.SET_NULL, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        if not self.building_assign_id:
            self.building_assign_id = generate_auto_id(BuildingAssign, "BLASS")
        super().save(*args, **kwargs)


class TaskAssign(models.Model):
    task_assign_id = models.CharField(max_length=50, primary_key=True, blank=True)
    task_hours = models.DecimalField(max_digits=6, decimal_places=2)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("inprogress", "In Progress"),
            ("completed", "Completed"),
            ("pending", "Pending"),
        ],
        default="pending",
    )
    priority = models.CharField(max_length=50, blank=True, null=True)
    # attachments = models.FileField(
    #     upload_to="tasks/attachments/", blank=True, null=True
    # )
    comments = models.TextField(blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    employee = models.ManyToManyField(Employee, blank=True)
    building_assign = models.ForeignKey(
        BuildingAssign, on_delete=models.SET_NULL, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        if not self.task_assign_id:
            self.task_assign_id = generate_auto_id(TaskAssign, "TKASS")
        super().save(*args, **kwargs)


class TimeSheet(models.Model):
    timesheet_id = models.CharField(max_length=50, primary_key=True, blank=True)
    employee = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, blank=True, null=True
    )
    task_assign = models.ForeignKey(TaskAssign, on_delete=models.SET_NULL, null=True)
    task_hours = models.DecimalField(max_digits=6, decimal_places=2)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    submitted = models.BooleanField(default=False, null=True, blank=True)
    approved = models.BooleanField(default=False, null=True, blank=True)
    rejected = models.BooleanField(default=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.timesheet_id:
            with transaction.atomic():
                last = TimeSheet.objects.select_for_update().aggregate(
                    models.Max("timesheet_id")
                )["timesheet_id__max"]

                if last:
                    last_num = int(last.split("_")[1])
                    self.timesheet_id = f"TS_{last_num + 1:015d}"
                else:
                    self.timesheet_id = "TS_000000000000001"
        super().save(*args, **kwargs)
        # -- CompOff eligibility check after saving --
        if self.date and self.employee:
            try:
                calendar = Calendar.objects.get(date=self.date)
                if calendar.is_weekend or calendar.is_holiday:

                    # # Check if already exists
                    # if not CompOffRequest.objects.filter(
                    #     employee=self.employee, date=self.date
                    # ).exists():
                    #     # Sum all task_hours for this employee and date

                    total_hours = (
                        TimeSheet.objects.filter(
                            employee=self.employee, date=self.date
                        ).aggregate(total=Sum("task_hours"))["total"]
                        or 0
                    )

                    # Match with comp off thresholds
                    compoff_entry = CompOff.objects.filter(
                        min_hours__lte=total_hours, max_hours__gte=total_hours
                    ).first()

                    if compoff_entry:
                        duration = (
                            1.0 if compoff_entry.leave_type == "full_day" else 0.5
                        )
                        # Create or update compoff request
                        # CompOffRequest.objects.create(
                        #     employee=self.employee,
                        #     date=self.date,
                        #     duration=duration,
                        #     reason=f"Worked on {'Weekend' if calendar.is_weekend else 'Holiday'}",
                        #     expiry_date=self.date + timedelta(days=30),
                        #     status="eligible",
                        # )
                        CompOffRequest.objects.update_or_create(
                            employee=self.employee,
                            date=self.date,
                            defaults={
                                "duration": duration,
                                "reason": f"Worked on {'Weekend' if calendar.is_weekend else 'Holiday'}",
                                "expiry_date": self.date + timedelta(days=30),
                                "status": "eligible",
                            },
                        )

                    else:
                        # No longer eligible — update existing request if present
                        CompOffRequest.objects.filter(
                            employee=self.employee, date=self.date
                        ).update(
                            duration=0,
                            status="expired",
                            reason="Hours dropped below comp off threshold",
                        )

            except Calendar.DoesNotExist:
                # Optional: log warning or skip silently
                pass


class Variation(models.Model):
    date = models.DateField(null=True, blank=True)
    title = models.CharField(max_length=50)
    hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True
    )


# Generic Attachment Model
class Attachment(models.Model):
    file = models.FileField(upload_to="attachments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Polymorphic relation to multiple models
    project = models.ForeignKey(
        "Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="Projectattachments",
    )
    task = models.ForeignKey(
        "Task",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="Taskattachments",
    )
    task_assign = models.ForeignKey(
        "TaskAssign",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="TaskAssignattachments",
    )
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="Employeeattachments",
    )
    leavestaken = models.ForeignKey(
        "LeavesTaken",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leaveattachments",
    )

    def __str__(self):
        return f"{self.file.name}"


# Generic Attachment Model
class EmployeeAttachment(models.Model):
    file = models.FileField(upload_to="attachments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    document_type = models.CharField(
        max_length=50,
        choices=[
            ("PAN", "PAN"),
            ("Aadhaar", "Aadhaar"),
            ("bank", "Bank Details"),
            ("Degree", "Degree certificate"),
            ("marksheets", "Marksheets"),
            ("resume", "Resume"),
            ("empletter", "Signed employment letter"),
            ("relievingletter", "Last company relieving letter"),
            ("payslip", "Last company Payslip"),
            ("idproof", "ID Proof"),
        ],
        blank=True,
        null=True,
    )

    employee = models.ForeignKey(
        "Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="Employeedetailsattachments",
    )

    def __str__(self):
        return f"{self.file.name}"


# Generic Attachment Model
class CompanyPolicy(models.Model):
    file = models.FileField(upload_to="attachments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    document_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    uploaded_by = models.ForeignKey(
        "Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="CompanyPolicy",
    )

    def __str__(self):
        return f"{self.file.name}"
