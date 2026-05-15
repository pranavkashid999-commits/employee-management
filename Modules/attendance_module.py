from Database.db import db
from datetime import date


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employee_details.id"),
        nullable=False
    )

    date = db.Column(db.Date, default=date.today, nullable=False)

    # P  = Present    → full pay
    # HD = Half Day   → 0.5 day deduction
    # A  = Absent     → paid up to 2/month, extra = deducted
    # SL = Sick Leave → always paid, no deduction
    status = db.Column(db.String(2), nullable=False)