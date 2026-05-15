from flask_restx import Namespace, Resource, fields
from flask import request
from services.employee_service import (
    create_employee,
    get_all_employees,
    get_employee_by_id,
    update_employee,
    delete_employee,
    get_employees_by_department,
    search_employee_by_name,
    search_employee_by_city,    # ✅ new
    search_employee_by_email    # ✅ new
)
from Utils.role_request import role_request

employee_rout = Namespace(
    "employee",
    description="employee_api"
)

employee_model = employee_rout.model(
    "Employee",
    {
        "name": fields.String(required=True),
        "city": fields.String(required=True),
        "email": fields.String(required=True),
        "salary": fields.Float(required=True),
        "department": fields.String(required=True)
    }
)

employee_update_model = employee_rout.model(
    "EmployeeUpdate",
    {
        "name": fields.String(),
        "city": fields.String(),
        "email": fields.String(),
        "salary": fields.Float(),
        "department": fields.String()
    }
)


@employee_rout.route("/add_emp")
class CreateEmployee(Resource):

    @employee_rout.expect(employee_model)
    @role_request(["superadmin", "admin"])
    def post(self):
        return create_employee(request.json)


@employee_rout.route("/get/all")
class GetAllEmployee(Resource):

    @role_request(["superadmin", "admin"])
    def get(self):
        return get_all_employees()


@employee_rout.route("/get/<int:emp_id>")
class GetEmployee(Resource):

    @role_request(["superadmin", "admin"])
    def get(self, emp_id):
        return get_employee_by_id(emp_id)


@employee_rout.route("/update/<int:emp_id>")
class UpdateEmployee(Resource):

    @employee_rout.expect(employee_update_model)
    @role_request(["superadmin", "admin"])
    def put(self, emp_id):
        return update_employee(emp_id, request.json)


@employee_rout.route("/delete/<int:emp_id>")
class DeleteEmployee(Resource):

    @role_request(["superadmin"])
    def delete(self, emp_id):
        return delete_employee(emp_id)


@employee_rout.route("/by-department/<string:dept_name>")
class EmployeeByDepartment(Resource):

    @role_request(["superadmin", "admin"])
    def get(self, dept_name):
        return get_employees_by_department(dept_name)


@employee_rout.route("/search/<string:name>")
class SearchEmployee(Resource):

    @role_request(["superadmin", "admin"])
    def get(self, name):
        return search_employee_by_name(name)
    

@employee_rout.route("/search/city/<string:city>")
class SearchByCity(Resource):

    @role_request(["superadmin", "admin"])
    def get(self, city):
        return search_employee_by_city(city)


# ✅ NEW
@employee_rout.route("/search/email/<string:email>")
class SearchByEmail(Resource):

    @role_request(["superadmin", "admin"])
    def get(self, email):
        return search_employee_by_email(email)