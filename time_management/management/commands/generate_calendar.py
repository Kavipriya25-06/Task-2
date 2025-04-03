from time_management.models import Calendar
from django.core.management.base import BaseCommand

from django.db import transaction
from datetime import date, timedelta


class Command(BaseCommand):
    help = "Generate calendar data between given start and end years (inclusive)."

    def add_arguments(self, parser):
        parser.add_argument("start_year", type=int, help="Start year for calendar data")
        parser.add_argument("end_year", type=int, help="End year for calendar data")

    def handle(self, *args, **options):
        start_year = options["start_year"]
        end_year = options["end_year"]

        if start_year > end_year:
            self.stdout.write(
                self.style.ERROR("Start year must be less than or equal to end year")
            )
            return

        start_date = date(start_year, 1, 1)
        end_date = date(end_year + 1, 1, 1)  # end of the last year
        current = start_date

        entries = []

        with transaction.atomic():
            last = Calendar.objects.all().order_by("-calendar_id").first()
            counter = int(last.calendar_id.split("_")[1]) + 1 if last else 1

            while current < end_date:
                weekday = current.weekday()  # Monday=0, Sunday=6
                # is_weekend = weekday >= 5
                is_weekend = False
                is_holiday = False
                notes = ""

                # Sunday
                if weekday == 6:
                    is_weekend = True
                    # notes = "Sunday"

                # 2nd or 4th Saturday
                if weekday == 5:
                    week_number = (current.day - 1) // 7 + 1
                    if week_number in [2, 4]:
                        is_weekend = True
                        # notes = f"{week_number} Saturday"

                entries.append(
                    Calendar(
                        calendar_id=f"CAL_{counter:05d}",
                        date=current,
                        year=current.year,
                        fiscal_year=current.year,  # You can change this if your fiscal year is April–March
                        month=current.month,
                        month_name=current.strftime("%B"),
                        day=current.day,
                        day_of_week=weekday,
                        day_name=current.strftime("%A"),
                        week_of_year=current.isocalendar()[1],
                        quarter=(current.month - 1) // 3 + 1,
                        is_weekend=is_weekend,
                        is_holiday=is_holiday,
                        notes=notes if is_holiday else "",
                    )
                )

                counter += 1
                current += timedelta(days=1)

            Calendar.objects.bulk_create(entries)

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Calendar data successfully generated from {start_year} to {end_year}."
            )
        )
