# apps/time_management/services/leave_ledger.py
from decimal import Decimal
from dataclasses import dataclass
from typing import List
from django.db.models import Sum
from django.db.models.functions import ExtractYear, ExtractMonth
from ..models import LeaveOpeningBalance, LeaveDay

LEAVE_FIELDS = ("casual", "sick", "comp_off", "earned")


@dataclass
class MonthlyLine:
    month: int
    opening: dict  # {type: Decimal}
    availed: dict  # {type: Decimal}
    closing: dict  # {type: Decimal}


def _zero_dict():
    from decimal import Decimal

    return {t: Decimal("0.0") for t in LEAVE_FIELDS}


def get_monthly_leave_report(employee_id: int, year: int) -> List[MonthlyLine]:
    # 1) opening for the year
    try:
        ob = LeaveOpeningBalance.objects.get(employee_id=employee_id, year=year)
    except LeaveOpeningBalance.DoesNotExist:
        # Treat missing opening as zeros
        class _Zero:
            pass

        ob = _Zero()
        ob.casual_leave_opening = ob.sick_leave_opening = ob.comp_off_opening = (
            ob.earned_leave_opening
        ) = Decimal("0.0")

    opening = {
        "casual": ob.casual_leave_opening,
        "sick": ob.sick_leave_opening,
        "comp_off": ob.comp_off_opening,
        "earned": ob.earned_leave_opening,
    }

    # 2) monthly availed from approved LeaveDay
    rows = (
        LeaveDay.objects.approved()
        .filter(employee_id=employee_id, date__year=year)
        .values(month=ExtractMonth("date"), leave_type="leave_type")
        .annotate(total=Sum("duration"))
    )

    # Normalize monthly totals per type
    monthly_availed = {m: _zero_dict() for m in range(1, 13)}
    FIELD_MAP = {
        "casual": "casual",
        "sick": "sick",
        "comp_off": "comp_off",
        "earned": "earned",
    }
    for r in rows:
        m = int(r["month"])
        t = FIELD_MAP.get(r["leave_type"])
        if t:
            monthly_availed[m][t] = r["total"] or Decimal("0.0")

    # 3) walk months, carry forward closings
    lines: List[MonthlyLine] = []
    running_opening = opening.copy()

    for m in range(1, 13):
        av = monthly_availed[m]
        closing = {t: (running_opening[t] - av[t]) for t in LEAVE_FIELDS}
        lines.append(
            MonthlyLine(
                month=m,
                opening=running_opening.copy(),
                availed=av.copy(),
                closing=closing.copy(),
            )
        )
        # next month opening = this month closing
        running_opening = closing

    return lines
