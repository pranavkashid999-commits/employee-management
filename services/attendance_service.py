from Modules.attendance_module import Attendance
from Modules.employee_module import Employee
from Database.db import db
from datetime import date, datetime
import calendar
from sqlalchemy import extract
from Utils.responce import SUCCESS_RESPONCE, ERROR_RESPONCE

PAID_LEAVES_PER_MONTH = 2

VALID_STATUSES = {"P", "HD", "A", "SL"}


def mark_attendance_and_get_salary(employee_id, status):

    today = date.today()
    now   = datetime.now()

    if status not in VALID_STATUSES:
        return ERROR_RESPONCE(
            f"Invalid attendance status. Use one of: {', '.join(VALID_STATUSES)}",
            400
        )

    existing = Attendance.query.filter_by(
        employee_id=employee_id,
        date=today
    ).first()

    if existing:
        return ERROR_RESPONCE("Attendance already marked today", 400)

    employee = Employee.query.get(employee_id)
    if not employee:
        return ERROR_RESPONCE("Employee not found", 404)

    # ✅ दुपारी 12 नंतर P दिला तर automatically HD होईल
    if now.hour >= 12 and status == "P":
        status = "HD"

    attendance = Attendance(
        employee_id=employee_id,
        status=status
    )

    db.session.add(attendance)
    db.session.commit()

    return get_monthly_salary(employee_id, today.year, today.month)


def get_monthly_salary(employee_id, year=None, month=None):
    if year is None or month is None:
        today = date.today()
        year, month = today.year, today.month

    employee = Employee.query.get(employee_id)
    if not employee:
        return ERROR_RESPONCE("Employee not found", 404)

    days_in_month = calendar.monthrange(year, month)[1]

    records = Attendance.query.filter(
        Attendance.employee_id == employee_id,
        extract('year',  Attendance.date) == year,
        extract('month', Attendance.date) == month
    ).all()

    total_deduction_days = 0.0
    paid_leave_used      = 0
    sick_leave_used      = 0
    half_days            = 0
    absent_days          = 0

    for record in records:
        if record.status == "P":
            pass

        elif record.status == "SL":
            sick_leave_used += 1  # always paid

        elif record.status == "HD":
            half_days += 1
            total_deduction_days += 0.5

        elif record.status == "A":
            absent_days += 1
            paid_leave_used += 1
            if paid_leave_used > PAID_LEAVES_PER_MONTH:
                total_deduction_days += 1.0

    per_day_salary = employee.salary / days_in_month
    salary_cut     = total_deduction_days * per_day_salary
    final_salary   = employee.salary - salary_cut

    return SUCCESS_RESPONCE(
        "Monthly salary details",
        {
            "employee_id":          employee.id,
            "employee_name":        employee.name,
            "month":                f"{year}-{str(month).zfill(2)}",
            "days_in_month":        days_in_month,
            "base_salary":          employee.salary,
            "per_day_salary":       round(per_day_salary, 2),

            "half_days":            half_days,
            "sick_leave_used":      sick_leave_used,
            "absent_days":          absent_days,
            "paid_absents_allowed": PAID_LEAVES_PER_MONTH,
            "extra_absents_cut":    max(0, paid_leave_used - PAID_LEAVES_PER_MONTH),

            "total_deduction_days": total_deduction_days,
            "salary_cut":           round(salary_cut, 2),
            "final_salary":         round(final_salary, 2)
        }
    )


def get_today_summary():

    today = date.today()

    present  = Attendance.query.filter_by(date=today, status="P").count()
    half_day = Attendance.query.filter_by(date=today, status="HD").count()
    absent   = Attendance.query.filter_by(date=today, status="A").count()
    sick     = Attendance.query.filter_by(date=today, status="SL").count()

    total_marked = present + half_day + absent + sick

    return SUCCESS_RESPONCE(
        "Today attendance summary",
        {
            "date":         str(today),
            "present":      present,
            "half_day":     half_day,
            "absent":       absent,
            "sick_leave":   sick,
            "total_marked": total_marked
        }
    )