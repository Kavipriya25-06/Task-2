# apps/time_management/querysets.py
from django.db.models import QuerySet


class LeaveDayQuerySet(QuerySet):
    def approved(self):
        return self.filter(status="approved")
