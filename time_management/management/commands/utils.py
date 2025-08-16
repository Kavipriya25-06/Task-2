from time_management.models import LeavesAvailable
from datetime import date


def calculate_leave_entitlement(join_date: date) -> int:
    """
    Calculate leave entitlement based on 2-month intervals.
    """
    month = join_date.month
    interval = (month - 1) // 2  # Jan–Feb = 0, Mar–Apr = 1, ..., Nov–Dec = 5
    return max(6.5 - (join_date.month * 0.5), 0.5)
    # return max(6 - interval, 1)  # Never less than 1


def create_or_update_leaves_for_employee(emp, is_update=False):
    # if LeavesAvailable.objects.filter(employee=emp).exists():
    #     return False  # Already exists

    today = date.today()
    join_date = emp.doj
    if not join_date or not emp.employment_type:
        return False

    effective_type = emp.employment_type
    # if (
    #     emp.employment_type == "Probation"
    #     and emp.probation_confirmation_date
    #     and today >= emp.probation_confirmation_date
    # ):
    #     effective_type = "Fulltime"
    #     join_date = emp.probation_confirmation_date

    if (
        emp.employment_type == "Fulltime"
        and emp.probation_confirmation_date
        and today >= emp.probation_confirmation_date
    ):
        # When fulltime confirmed from probation
        join_date = emp.probation_confirmation_date

    sick_leave = casual_leave = earned_leave = 0

    if effective_type == "Fulltime":
        leave_count = calculate_leave_entitlement(join_date)
        sick_leave = casual_leave = earned_leave = leave_count

    elif effective_type == "Probation":
        end_date = emp.probation_confirmation_date
        if end_date and end_date > join_date:
            months = (
                (end_date.year - join_date.year) * 12
                + (end_date.month - join_date.month)
                + 1
            )
            casual_leave = months

    elif effective_type == "Contract":
        end_date = emp.contract_end_date
        if end_date and end_date > join_date:
            months = (
                (end_date.year - join_date.year) * 12
                + (end_date.month - join_date.month)
                + 1
            )
            casual_leave = months

    # No leave for Internship

    # LeavesAvailable.objects.create(
    #     employee=emp,
    #     sick_leave=sick_leave,
    #     casual_leave=casual_leave,
    #     comp_off=comp_off,
    #     earned_leave=earned_leave,
    # )

    leave_obj, created = LeavesAvailable.objects.get_or_create(employee=emp)

    leave_obj.sick_leave = sick_leave
    leave_obj.casual_leave = casual_leave
    leave_obj.earned_leave = earned_leave
    # leave_obj.comp_off = comp_off
    leave_obj.save()
    return True
