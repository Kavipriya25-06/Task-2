from datetime import date


def calculate_leave_entitlement(join_date: date) -> int:
    """
    Calculate leave entitlement based on 2-month intervals.
    """
    month = join_date.month
    interval = (month - 1) // 2  # Jan–Feb = 0, Mar–Apr = 1, ..., Nov–Dec = 5
    return max(6 - interval, 1)  # Never less than 1
