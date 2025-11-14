# import csv
# from django.core.management.base import BaseCommand

# # from myapp.models import Employee  # Import your Employee model
# from time_management.models import Employee  # Update the import based on your app name


# class Command(BaseCommand):
#     help = "Import employee data from CSV and update existing records"

#     def handle(self, *args, **kwargs):
#         # Path to your CSV file
#         csv_file_path = "employee_details_server_copy.csv"

#         # Open CSV file
#         with open(csv_file_path, mode="r") as file:
#             reader = csv.DictReader(file)

#             for row in reader:
#                 # Try to get the existing Employee record by employee_id or employee_code (unique fields)
#                 employee_id = row["employee_id"]
#                 employee_code = row.get("employee_code", None)
#                 employee_email = row.get("employee_email", None)

#                 # Try to get the employee using the employee_id or employee_code or employee_email
#                 employee, created = Employee.objects.update_or_create(
#                     employee_id=employee_id,
#                     defaults={
#                         "employee_code": employee_code,
#                         "employee_name": row.get("employee_name", ""),
#                         "last_name": row.get("last_name", ""),
#                         "fathers_name": row.get("fathers_name", ""),
#                         "gender": row.get("gender", ""),
#                         "dob": row.get("dob", None),
#                         "age": row.get("age", 0),
#                         "doj": row.get("doj", None),
#                         "contact_number": row.get("contact_number", ""),
#                         "identification_marks": row.get("identification_marks", ""),
#                         "wedding_date": row.get("wedding_date", None),
#                         "marital_status": row.get("marital_status", ""),
#                         "personal_email": row.get("personal_email", ""),
#                         "aadhaar_number": row.get("aadhaar_number", ""),
#                         "PAN": row.get("PAN", ""),
#                         "UAN": row.get("UAN", ""),
#                         "pf_number": row.get("pf_number", ""),
#                         "esi_number": row.get("esi_number", ""),
#                         "passport_number": row.get("passport_number", ""),
#                         "passport_validity": row.get("passport_validity", None),
#                         "onboarding_status": row.get("onboarding_status", 0.0),
#                         "status": row.get("status", ""),
#                         "remarks": row.get("remarks", ""),
#                         "location": row.get("location", ""),
#                         "permanent_address": row.get("permanent_address", ""),
#                         "local_address": row.get("local_address", ""),
#                         "employment_type": row.get("employment_type", ""),
#                         "designation": row.get("designation", ""),
#                         "source_of_hire": row.get("source_of_hire", ""),
#                         "department": row.get("department", ""),
#                         "qualification": row.get("qualification", ""),
#                         "year_of_passing": row.get("year_of_passing", 0),
#                         "previous_company_name": row.get("previous_company_name", ""),
#                         "previous_experience": row.get("previous_experience", 0),
#                         "aero360_experience": row.get("aero360_experience", 0),
#                         "total_experience": row.get("total_experience", 0),
#                         "experience_in_years": row.get("experience_in_years", 0.0),
#                         "probation_confirmation_date": row.get(
#                             "probation_confirmation_date", None
#                         ),
#                         "contract_end_date": row.get("contract_end_date", None),
#                         "employee_email": row.get("employee_email", ""),
#                         "reporting_manager": row.get("reporting_manager", ""),
#                         "second_reporting_manager": row.get(
#                             "second_reporting_manager", ""
#                         ),
#                         "resignation_date": row.get("resignation_date", None),
#                         "relieving_date": row.get("relieving_date", None),
#                         "seating_location": row.get("seating_location", ""),
#                         "work_phone": row.get("work_phone", ""),
#                         "extension": row.get("extension", ""),
#                         "account_number": row.get("account_number", ""),
#                         "ifsc_code": row.get("ifsc_code", ""),
#                         "bank_name": row.get("bank_name", ""),
#                         "bank_branch_name": row.get("bank_branch_name", ""),
#                         "bank_address": row.get("bank_address", ""),
#                         "emergency_contact_name": row.get("emergency_contact_name", ""),
#                         "emergency_contact_relationship": row.get(
#                             "emergency_contact_relationship", ""
#                         ),
#                         "emergency_contact_number": row.get(
#                             "emergency_contact_number", ""
#                         ),
#                         "blood_group": row.get("blood_group", ""),
#                         "profile_picture": row.get("profile_picture", None),
#                     },
#                 )

#                 if created:
#                     self.stdout.write(f"Created new employee: {employee_id}")
#                 else:
#                     self.stdout.write(f"Updated employee: {employee_id}")


import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from time_management.models import Employee


def parse_date(value):
    """Return a date or None (handles NULL/blank/mixed formats)."""
    if not value or str(value).strip().upper() in {"NULL", "NONE", "N/A", "NA", ""}:
        return None
    v = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(v, fmt).date()
        except ValueError:
            continue
    # Not fatal—just report and move on
    return None


def null_or(value, default=None):
    """Convert common NULL-ish strings to default."""
    if value is None:
        return default
    s = str(value).strip()
    if s.upper() in {"NULL", "NONE", "N/A", "NA", ""}:
        return default
    return value


class Command(BaseCommand):
    help = "Import employee data from CSV and update existing records with summary"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            dest="csv_file_path",
            default="employee_details_server.csv",
            help="Path to CSV file",
        )
        parser.add_argument(
            "--max-errors",
            dest="max_errors",
            type=int,
            default=25,
            help="Stop printing detailed errors after this many (summary still shows totals).",
        )

    def handle(self, *args, **options):
        csv_file_path = options["csv_file_path"]
        max_errors = options["max_errors"]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        invalid_date_hits = 0
        error_rows = []  # collect (row_num, employee_id, error_message)

        # Helpful: list date field names in one place
        date_fields = {
            "dob",
            "doj",
            "wedding_date",
            "passport_validity",
            "probation_confirmation_date",
            "contract_end_date",
            "resignation_date",
            "relieving_date",
        }

        with open(csv_file_path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, start=2):  # header is line 1
                try:
                    employee_id = null_or(row.get("employee_id"))
                    if not employee_id:
                        skipped_count += 1
                        if len(error_rows) < max_errors:
                            error_rows.append((idx, None, "Missing employee_id"))
                        continue

                    # Build defaults dict
                    defaults = {
                        "employee_code": null_or(row.get("employee_code")),
                        "employee_name": null_or(row.get("employee_name"), ""),
                        "last_name": null_or(row.get("last_name"), ""),
                        "fathers_name": null_or(row.get("fathers_name"), ""),
                        "gender": null_or(row.get("gender"), ""),
                        "age": null_or(row.get("age"), 0) or 0,
                        "contact_number": null_or(row.get("contact_number"), ""),
                        "identification_marks": null_or(
                            row.get("identification_marks"), ""
                        ),
                        "marital_status": null_or(row.get("marital_status"), ""),
                        "personal_email": null_or(row.get("personal_email"), ""),
                        "aadhaar_number": null_or(row.get("aadhaar_number"), ""),
                        "PAN": null_or(row.get("PAN"), ""),
                        "UAN": null_or(row.get("UAN"), ""),
                        "pf_number": null_or(row.get("pf_number"), ""),
                        "esi_number": null_or(row.get("esi_number"), ""),
                        "passport_number": null_or(row.get("passport_number"), ""),
                        "onboarding_status": null_or(row.get("onboarding_status"), 0.0)
                        or 0.0,
                        "status": null_or(row.get("status"), ""),
                        "remarks": null_or(row.get("remarks"), ""),
                        "location": null_or(row.get("location"), ""),
                        "permanent_address": null_or(row.get("permanent_address"), ""),
                        "local_address": null_or(row.get("local_address"), ""),
                        "employment_type": null_or(row.get("employment_type"), ""),
                        "designation": null_or(row.get("designation"), ""),
                        "source_of_hire": null_or(row.get("source_of_hire"), ""),
                        "department": null_or(row.get("department"), ""),
                        "qualification": null_or(row.get("qualification"), ""),
                        "year_of_passing": null_or(row.get("year_of_passing"), 0) or 0,
                        "previous_company_name": null_or(
                            row.get("previous_company_name"), ""
                        ),
                        "previous_experience": null_or(
                            row.get("previous_experience"), 0
                        )
                        or 0,
                        "aero360_experience": null_or(row.get("aero360_experience"), 0)
                        or 0,
                        "total_experience": null_or(row.get("total_experience"), 0)
                        or 0,
                        "experience_in_years": null_or(
                            row.get("experience_in_years"), 0.0
                        )
                        or 0.0,
                        "employee_email": null_or(row.get("employee_email"), ""),
                        "reporting_manager": null_or(row.get("reporting_manager"), ""),
                        "second_reporting_manager": null_or(
                            row.get("second_reporting_manager"), ""
                        ),
                        "seating_location": null_or(row.get("seating_location"), ""),
                        "work_phone": null_or(row.get("work_phone"), ""),
                        "extension": null_or(row.get("extension"), ""),
                        "account_number": null_or(row.get("account_number"), ""),
                        "ifsc_code": null_or(row.get("ifsc_code"), ""),
                        "bank_name": null_or(row.get("bank_name"), ""),
                        "bank_branch_name": null_or(row.get("bank_branch_name"), ""),
                        "bank_address": null_or(row.get("bank_address"), ""),
                        "emergency_contact_name": null_or(
                            row.get("emergency_contact_name"), ""
                        ),
                        "emergency_contact_relationship": null_or(
                            row.get("emergency_contact_relationship"), ""
                        ),
                        "emergency_contact_number": null_or(
                            row.get("emergency_contact_number"), ""
                        ),
                        "blood_group": null_or(row.get("blood_group"), ""),
                        "profile_picture": null_or(row.get("profile_picture")),
                    }

                    # Parse & assign all date fields
                    for field in date_fields:
                        raw = row.get(field)
                        parsed = parse_date(raw)
                        if (
                            parsed is None
                            and raw
                            and str(raw).strip()
                            not in {"", "NULL", "null", "None", "N/A", "NA"}
                        ):
                            invalid_date_hits += 1
                        defaults[field] = parsed

                    employee, was_created = Employee.objects.update_or_create(
                        employee_id=employee_id,
                        defaults=defaults,
                    )
                    if was_created:
                        created_count += 1
                    else:
                        updated_count += 1

                except Exception as e:
                    skipped_count += 1
                    if len(error_rows) < max_errors:
                        error_rows.append(
                            (
                                idx,
                                employee_id if "employee_id" in locals() else None,
                                str(e),
                            )
                        )

        # ---- Summary ----
        self.stdout.write("")
        self.stdout.write("===== Import Summary =====")
        self.stdout.write(f"CSV file           : {csv_file_path}")
        self.stdout.write(f"Created            : {created_count}")
        self.stdout.write(f"Updated            : {updated_count}")
        self.stdout.write(f"Skipped/Errors     : {skipped_count}")
        self.stdout.write(f"Invalid date hits  : {invalid_date_hits}")
        if error_rows:
            self.stdout.write("")
            self.stdout.write(
                "Some issues encountered (showing up to first {}):".format(max_errors)
            )
            for rownum, empid, msg in error_rows:
                self.stdout.write(f"  - Row {rownum} (employee_id={empid}): {msg}")
        self.stdout.write("==========================")
