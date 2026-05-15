from Database.db import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    employee_details = db.relationship(
        "Employee",
        backref="department",
        lazy=True
    )