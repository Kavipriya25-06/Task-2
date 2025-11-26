from rest_framework.viewsets import ModelViewSet
from ..models import (
    LeaveDay,
    Employee,
    Hierarchy,
    User,
    LeaveOpeningBalance,
    CompOffRequest,
)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from time_management.hierarchy.serializers import get_emp_under_manager
from time_management.leaveday.serializers import LeaveDaySerializer
from time_management.services.leave_ledger import get_monthly_leave_report
from decimal import Decimal
from django.db.models.functions import Coalesce

from django.db.models import Sum, Case, When, Value, F, DecimalField, Q


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def leave_day_api(request, id=None, employee_id=None):
    if request.method == "GET":
        if id:
            try:
                obj = LeaveDay.objects.get(id=id)
                serializer = LeaveDaySerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except LeaveDay.DoesNotExist:
                return Response(
                    {"error": "Leave record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        elif employee_id:
            try:
                obj = LeaveDay.objects.filter(employee=employee_id)
                serializer = LeaveDaySerializer(obj, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except LeaveDay.DoesNotExist:
                return Response(
                    {"error": "Employee Leave record not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            objs = LeaveDay.objects.all()
            serializer = LeaveDaySerializer(objs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = LeaveDaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Leave request submitted", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method in ["PUT", "PATCH"]:
        if not id:
            return Response(
                {"error": "Leave record ID is required for update"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = LeaveDay.objects.get(id=id)
        except LeaveDay.DoesNotExist:
            return Response(
                {"error": "Leave record not found"}, status=status.HTTP_404_NOT_FOUND
            )

        status_update = request.data.get("status")
        if status_update and status_update not in ["pending", "approved", "rejected"]:
            return Response(
                {"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = LeaveDaySerializer(
            obj, data=request.data, partial=(request.method == "PATCH")
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Leave request updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if not id:
            return Response(
                {"error": "Leave record ID is required for DELETE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            obj = LeaveDay.objects.get(id=id)
            obj.delete()
            return Response(
                {"message": "Leave request deleted"}, status=status.HTTP_204_NO_CONTENT
            )
        except LeaveDay.DoesNotExist:
            return Response(
                {"error": "Leave record not found"}, status=status.HTTP_404_NOT_FOUND
            )


def _zero():
    return Value(
        Decimal("0.0"), output_field=DecimalField(max_digits=6, decimal_places=1)
    )


@api_view(["GET"])
def leave_ledger_ytd(request, year: int):
    """
    Year-to-date leave ledger per employee.
    Query params:
      - month: optional int 1..12 (default 12). Aggregates availed/earned up to this month.
      - employee_id: optional filter to a single employee
    """
    try:
        upto_month = int(request.query_params.get("month", 12))
    except ValueError:
        upto_month = 12
    upto_month = max(1, min(12, upto_month))

    employee_id = request.query_params.get("employee_id")

    employees = Employee.objects.all()
    if employee_id:
        employees = employees.filter(employee_id=employee_id)

    # OPENING (per employee, by subquery join)
    # We annotate openings by joining LeaveOpeningBalance for the requested year.
    openings = LeaveOpeningBalance.objects.filter(employee_id=F("pk"), year=year)

    # AVAILED (approved LeaveDay within year and <= month)
    availed_filter = Q(
        leaveday__status="approved",
        leaveday__date__year=year,
        leaveday__date__month__lte=upto_month,
    )

    # If you accrue CompOff during the year via a CompOffRequest table, define a filter here.
    # Example (adjust to your schema):
    # earned_filter = Q(compoffrequest__status="approved",
    #                   compoffrequest__earn_date__year=year,
    #                   compoffrequest__earn_date__month__lte=upto_month)

    qs = (
        employees
        # OPENING annotations (coalesce to 0.0 if there's no opening row)
        .annotate(
            open_cl=Coalesce(
                LeaveOpeningBalance.objects.filter(
                    employee_id=F("pk"), year=year
                ).values("casual_leave_opening")[:1],
                _zero(),
            ),
            open_ml=Coalesce(
                LeaveOpeningBalance.objects.filter(
                    employee_id=F("pk"), year=year
                ).values("sick_leave_opening")[:1],
                _zero(),
            ),
            open_comp=Coalesce(
                LeaveOpeningBalance.objects.filter(
                    employee_id=F("pk"), year=year
                ).values("comp_off_opening")[:1],
                _zero(),
            ),
        )
        # AVAILED per type from LeaveDay
        .annotate(
            availed_cl=Coalesce(
                Sum(
                    Case(
                        When(
                            availed_filter & Q(leaveday__leave_type="casual"),
                            then="leaveday__duration",
                        ),
                        default=Value(0),
                        output_field=DecimalField(max_digits=6, decimal_places=1),
                    )
                ),
                _zero(),
            ),
            availed_ml=Coalesce(
                Sum(
                    Case(
                        When(
                            availed_filter & Q(leaveday__leave_type="sick"),
                            then="leaveday__duration",
                        ),
                        default=Value(0),
                        output_field=DecimalField(max_digits=6, decimal_places=1),
                    )
                ),
                _zero(),
            ),
            availed_comp=Coalesce(
                Sum(
                    Case(
                        When(
                            availed_filter & Q(leaveday__leave_type="comp_off"),
                            then="leaveday__duration",
                        ),
                        default=Value(0),
                        output_field=DecimalField(max_digits=6, decimal_places=1),
                    )
                ),
                _zero(),
            ),
        )
        # COMP-OFF EARNED during the year (set to zero if you don't track accruals)
        # If you do have a CompOffRequest model, replace co_earned with an annotated Sum similar to availed_* above.
        .annotate(co_earned=_zero())  # <-- replace with real accrual if available
        # BALANCES
        .annotate(
            bal_cl=F("open_cl") - F("availed_cl"),
            bal_ml=F("open_ml") - F("availed_ml"),
            bal_comp=F("open_comp") + F("co_earned") - F("availed_comp"),
        )
        .values(
            # —— Adjust these fields to your Employee model ——
            "employee_id",
            "employee_code",  # e.g., "DA0005"
            "employee_name",  # e.g., "Raju"
            "employment_type",  # e.g., "Full Time"
            "doj",  # joining date
            # openings
            "open_cl",
            "open_ml",
            "open_comp",
            # earned
            "co_earned",
            # availed
            "availed_cl",
            "availed_ml",
            "availed_comp",
            # balance
            "bal_cl",
            "bal_ml",
            "bal_comp",
        )
        .order_by("employee_code")
    )

    rows = list(qs)

    return Response(
        {"year": year, "upto_month": upto_month, "count": len(rows), "rows": rows}
    )


# hr/api/leave_opening_monthly.py
from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import Coalesce
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..models import LeaveOpeningBalance, LeaveDay

LEAVE_MAP = {
    "casual_leave": "casual_leave",
    "sick_leave": "sick_leave",
    "comp_off": "comp_off",
    "earned_leave": "earned_leave",
    "lop": "lop",
}


def _zero_dict():
    return {
        "casual_leave": Decimal("0.0"),
        "sick_leave": Decimal("0.0"),
        "comp_off": Decimal("0.0"),
        "earned_leave": Decimal("0.0"),
        "lop": Decimal("0.0"),
    }


@api_view(["GET"])
def opening_plus_monthly_availed(request, employee_id: str, year: int):
    """
    GET /api/leave/opening-monthly/<employee_id>/<year>/?month=8

    Returns:
      - opening (CL/ML/CompOff/Earned) for the year
      - availed for the given month (approved LeaveDay only)
      - remaining = opening - availed  (per category)
    """
    # ----- month param -----
    month_param = request.query_params.get("month")
    if not month_param:
        return Response(
            {"detail": "Query parameter 'month' is required (1..12)."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        month = int(month_param)
        if month < 1 or month > 12:
            raise ValueError
    except ValueError:
        return Response(
            {"detail": "Invalid 'month'. Use 1..12."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ----- opening row (or zeros) -----
    ob = LeaveOpeningBalance.objects.filter(employee_id=employee_id, year=year).first()
    opening = _zero_dict()
    balance_id = None
    if ob:
        opening = {
            "casual_leave": ob.casual_leave_opening or Decimal("0.0"),
            "sick_leave": ob.sick_leave_opening or Decimal("0.0"),
            "comp_off": ob.comp_off_opening or Decimal("0.0"),
            "earned_leave": ob.earned_leave_opening or Decimal("0.0"),
        }
        balance_id = ob.balance_id

    # ----- availed this month from approved LeaveDay -----
    month_rows = (
        LeaveDay.objects.filter(
            employee_id=employee_id,
            status="approved",
            date__year=year,
            date__month=month,
        )
        .values("leave_type")
        .annotate(total=Coalesce(Sum("duration"), Decimal("0.0")))
    )

    availed = _zero_dict()
    for r in month_rows:
        lt = r["leave_type"]  # expected: "casual"|"sick"|"comp_off"|"earned"
        if lt in availed:
            availed[lt] = r["total"] or Decimal("0.0")

    # ----- remaining = opening - availed (as requested) -----
    remaining = {t: (opening[t] - availed[t]) for t in opening.keys()}

    # ----- payload shaped like your table + computed fields -----
    payload = {
        "balance_id": balance_id,  # like LVOPN_00001 (may be null if no opening row)
        "employee_id": employee_id,
        "year": year,
        "month": month,
        # opening (like your DB screenshot)
        "casual_leave_opening": opening["casual_leave"],
        "sick_leave_opening": opening["sick_leave"],
        "comp_off_opening": opening["comp_off"],
        "earned_leave_opening": opening["earned_leave"],
        # availed for the given month
        "casual_leave_availed": availed["casual_leave"],
        "sick_leave_availed": availed["sick_leave"],
        "comp_off_availed": availed["comp_off"],
        "earned_leave_availed": availed["earned_leave"],
        "lop_availed": availed["lop"],
        # remaining = opening - availed
        "casual_leave_remaining": remaining["casual_leave"],
        "sick_leave_remaining": remaining["sick_leave"],
        "comp_off_remaining": remaining["comp_off"],
        "earned_leave_remaining": remaining["earned_leave"],
    }

    return Response(payload, status=200)


# hr/api/leave_opening_monthly_all.py
from decimal import Decimal
from django.db.models import (
    Sum,
    Case,
    When,
    Value,
    F,
    DecimalField,
    Q,
    Subquery,
    OuterRef,
)
from django.db.models.functions import Coalesce
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..models import Employee, LeaveOpeningBalance, LeaveDay, MonthlyLeaveBalance


def _zero():
    return Value(
        Decimal("0.0"), output_field=DecimalField(max_digits=6, decimal_places=1)
    )


@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def opening_plus_monthly_availed_all(request, year: int):
    """
    GET /api/leave/opening-monthly-all/<year>/?month=8
    Optional filters:
      - q=<text>        (search in code/name)
      - dept=<name>     (if you have department on Employee)
      - status=<name>   (employment type/status)

    Opening rule:
      opening(month) = previous month's MonthlyLeaveBalance.closing
        - if month>1: MLB(year, month-1)
        - if month==1: MLB(year-1, 12)
      Fallback for Jan: LeaveOpeningBalance(year); else 0.0
    """
    # ---- validate month ----
    m = request.query_params.get("month")
    if not m:
        return Response(
            {"detail": "Query parameter 'month' is required (1..12)."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        month = int(m)
        if not (1 <= month <= 12):
            raise ValueError
    except ValueError:
        return Response(
            {"detail": "Invalid 'month'. Use 1..12."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # prev period for opening
    if month == 1:
        prev_year = year - 1
        prev_month = 12
    else:
        prev_year = year
        prev_month = month - 1

    employees = Employee.objects.all()

    # ---- simple optional filters (adjust field names if different) ----
    q_text = request.query_params.get("q")
    if q_text:
        employees = employees.filter(
            Q(employee_code__icontains=q_text) | Q(employee_name__icontains=q_text)
        )
    dept = request.query_params.get("dept")
    if dept and hasattr(Employee, "department"):
        employees = employees.filter(department__iexact=dept)
    status_filter = request.query_params.get("status")
    if status_filter and hasattr(Employee, "employment_type"):
        employees = employees.filter(employment_type__iexact=status_filter)

    # --- Subqueries for OPENING from previous month's MonthlyLeaveBalance ---
    mlb_prev = MonthlyLeaveBalance.objects.filter(
        employee=OuterRef("pk"),
        year=prev_year,
        month=prev_month,
    )

    # For January only, allow fallback to LeaveOpeningBalance(year)
    lob_curr = None
    if month == 1:
        lob_curr = LeaveOpeningBalance.objects.filter(
            employee=OuterRef("pk"), year=year
        )

    # --- correlated subquery for OPENINGS (this is the key change) ---
    lob = LeaveOpeningBalance.objects.filter(employee=OuterRef("pk"), year=year)

    # ---- annotate OPENINGS (coalesce properly) ----
    # casual
    open_cl_expr = Coalesce(
        Subquery(mlb_prev.values("casual_leave_balance")[:1]),
        # Jan fallback to opening table:
        Subquery(lob_curr.values("casual_leave_opening")[:1]) if lob_curr else _zero(),
        _zero(),
    )
    # sick
    open_ml_expr = Coalesce(
        Subquery(mlb_prev.values("sick_leave_balance")[:1]),
        Subquery(lob_curr.values("sick_leave_opening")[:1]) if lob_curr else _zero(),
        _zero(),
    )
    # comp off
    open_comp_expr = Coalesce(
        Subquery(mlb_prev.values("comp_off_balance")[:1]),
        Subquery(lob_curr.values("comp_off_opening")[:1]) if lob_curr else _zero(),
        _zero(),
    )
    # earned
    open_earned_expr = Coalesce(
        Subquery(mlb_prev.values("earned_leave_balance")[:1]),
        Subquery(lob_curr.values("earned_leave_opening")[:1]) if lob_curr else _zero(),
        _zero(),
    )

    employees = employees.annotate(
        open_cl=open_cl_expr,
        open_ml=open_ml_expr,
        open_comp=open_comp_expr,
        open_earned=open_earned_expr,
    )

    # ---- annotate OPENINGS via subqueries (coalesce to 0.0) ----
    # employees = employees.annotate(
    #     open_cl=Coalesce(Subquery(lob.values("casual_leave_opening")[:1]), _zero()),
    #     open_ml=Coalesce(Subquery(lob.values("sick_leave_opening")[:1]), _zero()),
    #     open_comp=Coalesce(Subquery(lob.values("comp_off_opening")[:1]), _zero()),
    #     open_earned=Coalesce(Subquery(lob.values("earned_leave_opening")[:1]), _zero()),
    # )

    # ---- AVAILED for that month from approved LeaveDay (reverse rel: leaveday) ----
    approved_month = Q(
        leaveday__status="approved",
        leaveday__date__year=year,
        leaveday__date__month=month,
    )

    # employees = employees.annotate(
    #     availed_cl=Coalesce(
    #         Sum(
    #             Case(
    #                 When(
    #                     approved_month & Q(leaveday__leave_type="casual_leave"),
    #                     then=F("leaveday__duration"),
    #                 ),
    #                 default=Value(0),
    #                 output_field=DecimalField(max_digits=6, decimal_places=1),
    #             )
    #         ),
    #         _zero(),
    #     ),
    #     availed_ml=Coalesce(
    #         Sum(
    #             Case(
    #                 When(
    #                     approved_month & Q(leaveday__leave_type="sick_leave"),
    #                     then=F("leaveday__duration"),
    #                 ),
    #                 default=Value(0),
    #                 output_field=DecimalField(max_digits=6, decimal_places=1),
    #             )
    #         ),
    #         _zero(),
    #     ),
    #     availed_comp=Coalesce(
    #         Sum(
    #             Case(
    #                 When(
    #                     approved_month & Q(leaveday__leave_type="comp_off"),
    #                     then=F("leaveday__duration"),
    #                 ),
    #                 default=Value(0),
    #                 output_field=DecimalField(max_digits=6, decimal_places=1),
    #             )
    #         ),
    #         _zero(),
    #     ),
    #     availed_earned=Coalesce(
    #         Sum(
    #             Case(
    #                 When(
    #                     approved_month & Q(leaveday__leave_type="earned_leave"),
    #                     then=F("leaveday__duration"),
    #                 ),
    #                 default=Value(0),
    #                 output_field=DecimalField(max_digits=6, decimal_places=1),
    #             )
    #         ),
    #         _zero(),
    #     ),
    #     availed_lop=Coalesce(
    #         Sum(
    #             Case(
    #                 When(
    #                     approved_month & Q(leaveday__leave_type="lop"),
    #                     then=F("leaveday__duration"),
    #                 ),
    #                 default=Value(0),
    #                 output_field=DecimalField(max_digits=6, decimal_places=1),
    #             )
    #         ),
    #         _zero(),
    #     ),
    # )

    # # ---- Comp-Off Earned (approved this month) ----
    # employees = employees.annotate(
    #     comp_off_earned=Coalesce(
    #         Sum(
    #             Case(
    #                 When(
    #                     Q(compoffrequest__status="approved")
    #                     & Q(compoffrequest__date__year=year)
    #                     & Q(compoffrequest__date__month=month),
    #                     then=F("compoffrequest__duration"),
    #                 ),
    #                 default=Value(0),
    #                 output_field=DecimalField(max_digits=6, decimal_places=1),
    #             )
    #         ),
    #         _zero(),
    #     ),
    # )

    # --- BASE subqueries (one per metric) to avoid row multiplication ---
    ld_base = LeaveDay.objects.filter(
        employee=OuterRef("pk"),
        status="approved",
        date__year=year,
        date__month=month,
    )

    def sum_ld(leave_type):
        return (
            ld_base.filter(leave_type=leave_type)
            .values("employee_id")
            .annotate(total=Coalesce(Sum("duration"), Decimal("0.0")))
            .values("total")[:1]
        )

    # Per-type availed (month)
    sub_availed_cl = sum_ld("casual_leave")
    sub_availed_ml = sum_ld("sick_leave")
    sub_availed_comp = sum_ld("comp_off")
    sub_availed_earned = sum_ld("earned_leave")
    sub_availed_lop = sum_ld("lop")

    # Comp-off earned (approved credits this month)
    sub_comp_earned = (
        CompOffRequest.objects.filter(
            employee=OuterRef("pk"),
            status="approved",
            date__year=year,
            date__month=month,
        )
        .values("employee_id")
        .annotate(total=Coalesce(Sum("duration"), Decimal("0.0")))
        .values("total")[:1]
    )

    employees = employees.annotate(
        availed_cl=Coalesce(
            Subquery(
                sub_availed_cl,
                output_field=DecimalField(max_digits=6, decimal_places=1),
            ),
            _zero(),
        ),
        availed_ml=Coalesce(
            Subquery(
                sub_availed_ml,
                output_field=DecimalField(max_digits=6, decimal_places=1),
            ),
            _zero(),
        ),
        availed_comp=Coalesce(
            Subquery(
                sub_availed_comp,
                output_field=DecimalField(max_digits=6, decimal_places=1),
            ),
            _zero(),
        ),
        availed_earned=Coalesce(
            Subquery(
                sub_availed_earned,
                output_field=DecimalField(max_digits=6, decimal_places=1),
            ),
            _zero(),
        ),
        availed_lop=Coalesce(
            Subquery(
                sub_availed_lop,
                output_field=DecimalField(max_digits=6, decimal_places=1),
            ),
            _zero(),
        ),
        comp_off_earned=Coalesce(
            Subquery(
                sub_comp_earned,
                output_field=DecimalField(max_digits=6, decimal_places=1),
            ),
            _zero(),
        ),
    )

    # ---- REMAINING = OPENING − AVAILED ----
    employees = employees.annotate(
        bal_cl=F("open_cl") - F("availed_cl"),
        bal_ml=F("open_ml") - F("availed_ml"),
        # bal_comp=F("open_comp") + F("comp_off_earned") - F("availed_comp"),
        bal_comp=F("open_comp") - F("availed_comp"),
        bal_earned=F("open_earned") - F("availed_earned"),
    )

    # ---- shape rows (adjust Employee fields to match your schema) ----
    rows = list(
        employees.values(
            "employee_id",
            "employee_code",
            "employee_name",
            "last_name",
            "resignation_date",
            "employment_type",
            # "employment_type",  # or "status" if that's your field name
            "doj",
            # opening
            "open_cl",
            "open_ml",
            "open_comp",
            "open_earned",
            # availed for month
            "availed_cl",
            "availed_ml",
            "availed_comp",
            "availed_earned",
            "availed_lop",
            # remaining
            "bal_cl",
            "bal_ml",
            "bal_comp",
            "bal_earned",
        ).order_by("employee_code")
    )

    return Response(
        {"year": year, "month": month, "count": len(rows), "rows": rows}, status=200
    )
