from flask_restx import Namespace, Resource, fields
from flask import request
from Utils.role_request import role_request
from services.attendance_service import (
    mark_attendance_and_get_salary,
    get_monthly_salary,
    get_today_summary
)

attendance_rout = Namespace(
    "attendance",
    description="Attendance API"
)

attendance_model = attendance_rout.model(
    "Attendance",
    {
        "employee_id": fields.Integer(required=True),
        "status": fields.String(
            required=True,
            description="P = Present | HD = Half Day | A = Absent | SL = Sick Leave"
        )
    }
)

@attendance_rout.route("/mark")
class MarkAttendance(Resource):

    @attendance_rout.expect(attendance_model)

    @role_request(["superadmin", "admin"])
    def post(self):
        data = request.get_json()
        return mark_attendance_and_get_salary(
            employee_id=data["employee_id"],
            status=data["status"]
        )


@attendance_rout.route("/salary/<int:employee_id>")
class Salary(Resource):


    @role_request(["superadmin", "admin"])
    def get(self, employee_id):
        """
        Get monthly salary.
        Optional query params: ?year=2025&month=4
        Defaults to current month if not provided.
        """
        year  = request.args.get("year",  type=int)
        month = request.args.get("month", type=int)
        return get_monthly_salary(employee_id, year, month)


@attendance_rout.route("/today/summary")
class TodaySummary(Resource):
    
    @role_request(["superadmin", "admin"])
    def get(self):
        return get_today_summary()