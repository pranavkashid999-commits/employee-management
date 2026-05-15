from flask_restx import Namespace, Resource, fields
from flask import request
from services.deapartment_service import (
    create_department,
    get_all_departments,
    get_department_by_id,
    update_department,
    delete_department,
    search_department_by_name
)
from Utils.role_request import role_request

department_rout = Namespace(
    "department",
    description="department_api"
)

department_model = department_rout.model(
    "Department",
    {
        "name": fields.String(
            required=True,
            description="department name"
        )
    }
)


@department_rout.route("/add_dept")
class CreateDepartment(Resource):

    @department_rout.expect(department_model)
    @role_request(["superadmin", "admin"])
    def post(self):
        return create_department(request.json)


@department_rout.route("/all")
class GetAllDepartment(Resource):

    @role_request(["superadmin", "admin"])
    def get(self):
        return get_all_departments()


@department_rout.route("/<int:dept_id>")
class GetDepartment(Resource):

    @role_request(["superadmin", "admin"])
    def get(self, dept_id):
        return get_department_by_id(dept_id)


@department_rout.route("/update/<int:dept_id>")
class UpdateDepartment(Resource):

    @department_rout.expect(department_model)
    @role_request(["superadmin", "admin"])
    def put(self, dept_id):
        return update_department(dept_id, request.json)


@department_rout.route("/delete/<int:dept_id>")
class DeleteDepartment(Resource):

    @role_request(["superadmin"])
    def delete(self, dept_id):
        return delete_department(dept_id)


@department_rout.route("/search/<string:name>")
class SearchDepartment(Resource):

    @role_request(["superadmin", "admin"])
    def get(self, name):
        return search_department_by_name(name)