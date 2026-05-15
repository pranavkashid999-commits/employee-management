from flask import Flask
from flask_restx import Api
from flask_cors import CORS

# ================= DATABASE =================
from Database.db import db

# ================= MODELS ===================
from Modules.user_model import User
from Modules.department import Department
from Modules.employee_module import Employee
from Modules.attendance_module import Attendance

# ================= ROUTES ===================
from Routs.auth_routs import auth_routs
from Routs.department_rout import department_rout
from Routs.employee_rout import employee_rout
from Routs.attendance_rout import attendance_rout

# ================= CONFIG ===================
from config import Config


def create_app():
    app = Flask(__name__)

    # ---------- BASIC CONFIG ----------
    app.config.from_object(Config)
    app.secret_key = "super-secret-key"

    # ---------- CORS (VERY IMPORTANT) ----------
    CORS(
        app,
        supports_credentials=True,
        resources={r"/*": {"origins": "*"}}
    )

    # ---------- DATABASE INIT ----------
    db.init_app(app)

    # ---------- API INIT ----------
    api = Api(
        app,
        title="Employee Management System API",
        version="1.0",
        description="Auth | Employee | Department | Attendance | Salary",
        doc="/swagger"
    )

    # ---------- REGISTER NAMESPACES ----------
    api.add_namespace(auth_routs, path="/Auth")
    api.add_namespace(department_rout, path="/department")
    api.add_namespace(employee_rout, path="/employee")
    api.add_namespace(attendance_rout, path="/attendance")

    # ---------- CREATE TABLES ----------
    with app.app_context():
        db.create_all()

    return app


# ================= RUN ===================
if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=5002,
        debug=True
    )