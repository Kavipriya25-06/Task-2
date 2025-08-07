# time_management/management/commands/sync_intime_biometric.py

from django.core.management.base import BaseCommand
from django.db import transaction
from time_management.models import Employee, BiometricData

import requests
from datetime import datetime, timedelta, date
import logging
import os

from django.db.models import Q


class Command(BaseCommand):
    help = "Sync biometric attendance data from external API"

    def handle(self, *args, **options):
        self.stdout.write("Starting biometric data sync (API)...")

        # --- Setup logging with monthly rotation ---
        # log_dir = os.path.join(os.path.dirname(__file__), "../../../logs/")
        log_dir = "/tmp/biometric_logs"
        os.makedirs(log_dir, exist_ok=True)
        log_month = date.today().strftime("%Y-%m")
        log_file = os.path.join(log_dir, f"biometric_sync_{log_month}.log")

        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        logging.info("---- Biometric API sync started ----")

        # Get today's date
        today_str = date.today().strftime("%Y-%m-%d")

        # Use it in your API URL
        api_url = f"http://192.168.0.209:8001/api/attendance/{today_str}/"

        # --- 1️ Fetch JSON data from API ---
        try:
            # api_url = "http://192.168.0.10:8000/api/attendance/today/"
            response = requests.get(api_url)
            response.raise_for_status()
            biometric_rows = response.json()
        except Exception as e:
            error_msg = f"Failed to fetch data from API: {e}"
            self.stdout.write(self.style.ERROR(error_msg))
            logging.error(error_msg)
            return

        if not biometric_rows:
            msg = "No biometric records received from API."
            self.stdout.write(msg)
            logging.info(msg)
            return

        created_count = 0
        updated_count = 0

        # --- 2️ Process each row ---
        for row in biometric_rows:
            user_id = row.get("UserId")
            record_date = row.get("Date")
            first_in = row.get("First_In")
            last_out = row.get("Last_Out")

            try:
                employee = Employee.objects.get(employee_code=str(user_id))
            except Employee.DoesNotExist:
                warning_msg = f"Employee with code {user_id} not found. Skipping."
                self.stdout.write(self.style.WARNING(warning_msg))
                logging.warning(warning_msg)
                continue

            # --- 3️ Skip if first_in/last_out missing ---
            if not first_in:
                warning_msg = f"Skipping {user_id} on {record_date} — first_in or last_out missing."
                self.stdout.write(self.style.WARNING(warning_msg))
                logging.warning(warning_msg)
                continue

            # --- 4️ Parse datetimes and calculate work hours ---
            try:
                # Example first_in: "2025-05-08 09:36:02"
                first_in_dt = datetime.strptime(first_in, "%Y-%m-%dT%H:%M:%SZ")

                in_time_obj = first_in_dt.time()

            except Exception as e:
                error_msg = (
                    f"Datetime parsing error for {user_id} on {record_date}: {e}"
                )
                self.stdout.write(self.style.ERROR(error_msg))
                logging.error(error_msg)
                continue

            # --- 5️ Create or update BiometricData ---
            with transaction.atomic():
                # bio_obj, created = BiometricData.objects.get_or_create(
                #     employee=employee,
                #     date=record_date,
                #     defaults={
                #         "employee_code": employee.employee_code,
                #         "employee_name": employee.employee_name,
                #         "in_time": in_time_obj,
                #         "status": "Present",
                #         "remarks": "",
                #         "modified_by": None,
                #     },
                # )

                # if not created:
                qs = BiometricData.objects.filter(employee=employee, date=record_date)
                count = qs.count()

                if count > 1:
                    warning_msg = f"Multiple records for Employee={user_id}, Date={record_date}. Skipping."
                    self.stdout.write(self.style.WARNING(warning_msg))
                    logging.warning(warning_msg)
                    continue
                elif count == 1:
                    bio_obj = qs.first()
                    bio_obj.in_time = in_time_obj
                    bio_obj.status = "Present"
                    bio_obj.save()
                    updated_count += 1
                else:
                    BiometricData.objects.create(
                        employee=employee,
                        date=record_date,
                        employee_code=employee.employee_code,
                        employee_name=employee.employee_name,
                        in_time=in_time_obj,
                        status="Present",
                        remarks="",
                        modified_by=None,
                    )
                    created_count += 1

        summary = f"Sync complete. Created: {created_count}, Updated: {updated_count}"
        self.stdout.write(self.style.SUCCESS(summary))
        logging.info(summary)
        logging.info("---- Biometric API sync ended ----\n")
