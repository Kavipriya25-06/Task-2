from time_management.models import LeavesAvailable, Employee, LeaveOpeningBalance
from datetime import date
from decimal import Decimal


def calculate_leave_entitlement(join_date: date) -> int:
    """
    Calculate leave entitlement based on 2-month intervals.
    """
    month = join_date.month
    interval = (month - 1) // 2  # Jan–Feb = 0, Mar–Apr = 1, ..., Nov–Dec = 5
    return max(6.5 - (join_date.month * 0.5), 0.5)
    # return max(6 - interval, 1)  # Never less than 1


# def create_or_update_leaves_for_employee(emp, is_update=False):
#     # if LeavesAvailable.objects.filter(employee=emp).exists():
#     #     return False  # Already exists

#     today = date.today()
#     join_date = emp.doj
#     if not join_date or not emp.employment_type:
#         return False

#     effective_type = emp.employment_type
#     # if (
#     #     emp.employment_type == "Probation"
#     #     and emp.probation_confirmation_date
#     #     and today >= emp.probation_confirmation_date
#     # ):
#     #     effective_type = "Fulltime"
#     #     join_date = emp.probation_confirmation_date

#     if (
#         emp.employment_type == "Fulltime"
#         and emp.probation_confirmation_date
#         and today >= emp.probation_confirmation_date
#     ):
#         # When fulltime confirmed from probation
#         join_date = emp.probation_confirmation_date

#     sick_leave = casual_leave = earned_leave = 0

#     if effective_type == "Fulltime":
#         leave_count = calculate_leave_entitlement(join_date)
#         sick_leave = casual_leave = earned_leave = leave_count

#     elif effective_type == "Probation":
#         end_date = emp.probation_confirmation_date
#         if end_date and end_date > join_date:
#             months = (
#                 (end_date.year - join_date.year) * 12
#                 + (end_date.month - join_date.month)
#                 + 1
#             )
#             casual_leave = months

#     elif effective_type == "Contract":
#         end_date = emp.contract_end_date
#         if end_date and end_date > join_date:
#             months = (
#                 (end_date.year - join_date.year) * 12
#                 + (end_date.month - join_date.month)
#                 + 1
#             )
#             casual_leave = months

#     # No leave for Internship

#     # LeavesAvailable.objects.create(
#     #     employee=emp,
#     #     sick_leave=sick_leave,
#     #     casual_leave=casual_leave,
#     #     comp_off=comp_off,
#     #     earned_leave=earned_leave,
#     # )

#     leave_obj, created = LeavesAvailable.objects.get_or_create(employee=emp)

#     leave_obj.sick_leave = sick_leave
#     leave_obj.casual_leave = casual_leave
#     leave_obj.earned_leave = earned_leave
#     # leave_obj.comp_off = comp_off
#     leave_obj.save()
#     return True


FULLTIME_CL = Decimal("12.0")
FULLTIME_SL = Decimal("6.0")
FULLTIME_EL = Decimal("6.0")  # adjust if your policy differs


def prorated_entitlement(join_date: date, annual_value: Decimal) -> Decimal:
    """
    Pro-rate the annual leave based on the month of joining.
    Formula: (months remaining including join month / 12) * annual_value
    """
    months_remaining = 12 - join_date.month + 1
    pro_rata = (Decimal(months_remaining) / Decimal(12)) * annual_value
    # Round to nearest 0.5 (if you allow half-days)
    return pro_rata.quantize(Decimal("0.5"))


def create_or_update_leaves_for_employee(emp, is_update=False):
    today = date.today()
    join_date = emp.doj
    if not join_date or not emp.employment_type:
        return False

    effective_type = emp.employment_type

    sick_leave = casual_leave = earned_leave = Decimal("0.0")

    if effective_type == "Fulltime":
        # --- PRO-RATA LOGIC ---
        if join_date.year == today.year:
            casual_leave = prorated_entitlement(join_date, FULLTIME_CL)
            sick_leave = prorated_entitlement(join_date, FULLTIME_SL)
            earned_leave = prorated_entitlement(join_date, FULLTIME_EL)
        else:
            # Joined in a previous year → full entitlement
            casual_leave = FULLTIME_CL
            sick_leave = FULLTIME_SL
            earned_leave = FULLTIME_EL

    elif effective_type == "Probation":
        # Same as before: accrual based on months until confirmation
        end_date = emp.probation_confirmation_date
        if end_date and end_date > join_date:
            months = (
                (end_date.year - join_date.year) * 12
                + (end_date.month - join_date.month)
                + 1
            )
            casual_leave = Decimal(str(months))

    elif effective_type == "Contract":
        # Same as before: accrual per contract duration
        end_date = emp.contract_end_date
        if end_date and end_date > join_date:
            months = (
                (end_date.year - join_date.year) * 12
                + (end_date.month - join_date.month)
                + 1
            )
            casual_leave = Decimal(str(months))

    # Update LeavesAvailable snapshot
    leave_obj, _ = LeavesAvailable.objects.get_or_create(employee=emp)
    leave_obj.sick_leave = sick_leave
    leave_obj.casual_leave = casual_leave
    leave_obj.earned_leave = earned_leave
    leave_obj.save(update_fields=["sick_leave", "casual_leave", "earned_leave"])

    # Optionally sync the opening balance for current year
    year = today.year
    lob, _ = LeaveOpeningBalance.objects.get_or_create(
        employee=emp,
        year=year,
        defaults=dict(
            sick_leave_opening=sick_leave,
            casual_leave_opening=casual_leave,
            earned_leave_opening=earned_leave,
            comp_off_opening=Decimal("0.0"),
        ),
    )
    lob.sick_leave_opening = sick_leave
    lob.casual_leave_opening = casual_leave
    lob.earned_leave_opening = earned_leave
    lob.save(
        update_fields=[
            "sick_leave_opening",
            "casual_leave_opening",
            "earned_leave_opening",
        ]
    )

    return True


from datetime import date
from decimal import Decimal, ROUND_HALF_UP

FULL_CL = Decimal("12.0")
FULL_SL = Decimal("6.0")
CL_PER_MONTH = Decimal("1.0")
SL_PER_MONTH = Decimal("0.5")


def _months_inclusive_from(month: int) -> int:
    """Return how many months remain in the year including `month` (1..12)."""
    if month < 1 or month > 12:
        return 0
    return 12 - month + 1


def _q05(x: Decimal) -> Decimal:
    """Round to nearest 0.5 step if you want half-day granularity; else remove."""
    return (x * 2).to_integral_value(rounding=ROUND_HALF_UP) / Decimal(2)


def compute_year_entitlement_for_employee(
    emp,
    year: int,
    *,
    enforce_confirmation_for_fulltime: bool = True,
) -> tuple[Decimal, Decimal]:
    """
    Returns (CL_entitlement, SL_entitlement) for the given employee in a given year
    under policy: 12 CL, 6 SL per year; pro-rata if joined that year; full if prior year.
    If `enforce_confirmation_for_fulltime` is True, the “effective start” is the
    confirmation month when a probationer becomes Fulltime within that year.
    """
    doj = emp.doj
    if not doj:
        return Decimal("0"), Decimal("0")

    # Decide effective start date for the year's entitlement
    effective_start = doj

    # If you want to start entitlements from confirmation month (common policy):
    if enforce_confirmation_for_fulltime:
        if (
            emp.employment_type in ("Probation", "Fulltime")
            and emp.probation_confirmation_date
        ):
            # If confirmation happens in or before the target year, use it
            conf = emp.probation_confirmation_date
            if conf and conf.year == year:
                effective_start = conf
            elif conf and conf.year < year:
                # Confirmed in a previous year → full for this year
                effective_start = date(year, 1, 1)

    # Joined before this year (or effectively started before Jan of this year) → full
    if effective_start.year < year:
        return FULL_CL, FULL_SL

    # Joined after this year → nothing
    if effective_start.year > year:
        return Decimal("0"), Decimal("0")

    # Joined in this year → pro-rata
    months = _months_inclusive_from(effective_start.month)
    cl = CL_PER_MONTH * Decimal(months)
    sl = SL_PER_MONTH * Decimal(months)

    # If you want half-day steps, keep _q05; else just return cl, sl
    return _q05(cl), _q05(sl)
