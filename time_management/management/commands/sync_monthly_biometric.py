#

from django.core.management.base import BaseCommand
from django.db import transaction
from time_management.models import Employee, BiometricData

import requests
from datetime import datetime, timedelta, date
import logging
import os


class Command(BaseCommand):
    help = "Sync biometric attendance data from external API"

    def handle(self, *args, **options):
        self.stdout.write("Starting biometric data sync (API)...")

        # ---  Setup logging with monthly rotation ---
        log_dir = os.path.join(os.path.dirname(__file__), "../../../logs/")
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

        # Process the last 30 days (excluding today)
        start_date = datetime.today().date() - timedelta(days=30)
        end_date = datetime.today().date() - timedelta(days=1)

        total_created = 0
        total_updated = 0

        # Get yesterday's date
        # yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        # Use it in your API URL
        # api_url = f"http://192.168.0.209:8001/api/attendance/{yesterday}/"

        for single_date in (
            start_date + timedelta(n) for n in range((end_date - start_date).days + 1)
        ):
            date_str = single_date.strftime("%Y-%m-%d")
            api_url = f"http://192.168.0.209:8001/api/attendance/{date_str}/"
            self.stdout.write(f"Fetching data for {date_str}")
            logging.info(f"Fetching data for {date_str}")
            # --- 1 Fetch JSON data from API ---
            try:
                # api_url = "http://192.168.0.10:8000/api/attendance/today/"
                response = requests.get(api_url)
                response.raise_for_status()
                biometric_rows = response.json()
            except Exception as e:
                error_msg = f"Failed to fetch data from API: {e}"
                self.stdout.write(self.style.ERROR(error_msg))
                logging.error(error_msg)
                continue

            if not biometric_rows:
                msg = "No biometric records received from API."
                self.stdout.write(msg)
                logging.info(msg)
                continue

            created_count = 0
            updated_count = 0

            # --- 2 Process each row ---
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

                # --- 3 Skip if first_in/last_out missing ---
                if not first_in or not last_out:
                    warning_msg = f"Skipping {user_id} on {record_date} — first_in or last_out missing."
                    self.stdout.write(self.style.WARNING(warning_msg))
                    logging.warning(warning_msg)
                    continue

                # --- 4 Parse datetimes and calculate work hours ---
                try:
                    # Example first_in: "2025-05-08 09:36:02"
                    first_in_dt = datetime.strptime(first_in, "%Y-%m-%dT%H:%M:%SZ")
                    last_out_dt = datetime.strptime(last_out, "%Y-%m-%dT%H:%M:%SZ")

                    in_time_obj = first_in_dt.time()
                    out_time_obj = last_out_dt.time()

                    # If out_time is earlier than in_time (overnight shift correction)
                    if last_out_dt < first_in_dt:
                        last_out_dt += timedelta(days=1)

                    work_hours = (last_out_dt - first_in_dt).total_seconds() / 3600

                except Exception as e:
                    error_msg = (
                        f"Datetime parsing error for {user_id} on {record_date}: {e}"
                    )
                    self.stdout.write(self.style.ERROR(error_msg))
                    logging.error(error_msg)
                    continue

                # --- 5 Create or update BiometricData ---
                with transaction.atomic():
                    bio_obj, created = BiometricData.objects.get_or_create(
                        employee=employee,
                        date=record_date,
                        defaults={
                            "employee_code": employee.employee_code,
                            "employee_name": employee.employee_name,
                            "in_time": in_time_obj,
                            "out_time": out_time_obj,
                            "work_duration": round(work_hours, 2),
                            "ot": 0,
                            "total_duration": round(work_hours, 2),
                            "status": "Present",
                            "remarks": "",
                            "modified_by": None,
                        },
                    )

                    if not created:
                        # bio_obj.in_time = in_time_obj
                        bio_obj.out_time = out_time_obj
                        bio_obj.work_duration = round(work_hours, 2)
                        bio_obj.total_duration = round(work_hours, 2)
                        bio_obj.status = "Present"
                        bio_obj.save()
                        updated_count += 1
                    else:
                        created_count += 1

            total_created += created_count
            total_updated += updated_count

        summary = f"30-day sync complete. Total Created: {total_created}, Total Updated: {total_updated}"

        self.stdout.write(self.style.SUCCESS(summary))
        logging.info(summary)
        logging.info("---- Biometric API sync ended ----\n")
