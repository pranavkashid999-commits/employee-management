from Database.db import db
from datetime import datetime


class Employee(db.Model):
    __tablename__ = "employee_details"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    salary = db.Column(db.Float, nullable=False)

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)