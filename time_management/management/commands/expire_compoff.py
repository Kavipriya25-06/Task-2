from django.core.management.base import BaseCommand
from django.utils import timezone
from time_management.models import CompOffRequest


class Command(BaseCommand):
    help = "Marks CompOffRequests as expired if their expiry_date has passed and status is not already 'expired'."

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        expired_qs = CompOffRequest.objects.filter(expiry_date__lt=today).exclude(
            status="expired"
        )

        total = expired_qs.count()
        if total == 0:
            self.stdout.write(
                self.style.SUCCESS("No comp-off requests to expire today.")
            )
            return

        expired_qs.update(status="expired")
        self.stdout.write(
            self.style.SUCCESS(f"Successfully expired {total} comp-off request(s).")
        )
