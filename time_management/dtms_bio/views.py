from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import connection, connections
from datetime import datetime


# GET /api/dtms_event_time/2025-08-07/
@api_view(["GET"])
def dtms_event_time(request, date_str=None):
    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "Invalid date format"}, status=400)

    sql = """
        SELECT 
            EMPCode,
            PunchDateTime,
            INOutType,
            DownloadDatetime
        FROM sync_DTMS_bio
        WHERE DATE(PunchDateTime) = %s
        ORDER BY PunchDateTime
    """
    with connections["reporting"].cursor() as cursor:
        cursor.execute(sql, [selected_date])
        rows = cursor.fetchall()

    columns = ["EmpCode", "PunchDateTime", "InOutType", "DownloadDateTime"]
    result = [dict(zip(columns, row)) for row in rows]
    return Response(result)


# GET /api/dtms_event_summary/2025-08-07/
@api_view(["GET"])
def dtms_event_summary(request, date_str=None):
    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "Invalid date format"}, status=400)

    sql = """
        SELECT 
            EMPCode,
            MIN(CASE WHEN INOutType = 0 THEN PunchDateTime END) AS FirstIn,
            MAX(CASE WHEN INOutType = 1 THEN PunchDateTime END) AS LastOut
        FROM sync_DTMS_bio
        WHERE DATE(PunchDateTime) = %s
        GROUP BY EMPCode
        ORDER BY EMPCode
    """
    with connections["reporting"].cursor() as cursor:
        cursor.execute(sql, [selected_date])
        rows = cursor.fetchall()

    columns = ["EmpCode", "FirstIn", "LastOut", "Date"]
    result = [dict(zip(columns, list(row) + [selected_date])) for row in rows]
    return Response(result)
