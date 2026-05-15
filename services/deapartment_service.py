from Modules.department import Department
from Database.db import db
from Utils.responce import SUCCESS_RESPONCE, ERROR_RESPONCE
from Utils.validation import validate_department

def create_department(data):
    error = validate_department(data)
    if error:
        return ERROR_RESPONCE(error, 400)

    dept = Department.query.filter_by(name=data["name"]).first()
    if dept:
        return ERROR_RESPONCE("department already exist", 400)

    department = Department(name=data["name"])
    db.session.add(department)
    db.session.commit()

    return SUCCESS_RESPONCE(
        "Department created successfully",
        {"id": department.id, "name": department.name}
    )

def get_all_departments():
    depts = Department.query.all()
    data = [{"id": d.id, "name": d.name} for d in depts]
    return SUCCESS_RESPONCE("Department list", data)

def get_department_by_id(dept_id):
    dept = Department.query.get(dept_id)
    if not dept:
        return ERROR_RESPONCE("Department not found", 404)

    return SUCCESS_RESPONCE(
        "Department details",
        {"id": dept.id, "name": dept.name}
    )

def update_department(dept_id, data):
    dept = Department.query.get(dept_id)
    if not dept:
        return ERROR_RESPONCE("Department not found", 404)

    dept.name = data.get("name", dept.name)
    db.session.commit()
    return SUCCESS_RESPONCE("Department updated successfully")

def delete_department(dept_id):
    dept = Department.query.get(dept_id)
    if not dept:
        return ERROR_RESPONCE("Department not found", 404)

    db.session.delete(dept)
    db.session.commit()
    return SUCCESS_RESPONCE("Department deleted successfully")

def search_department_by_name(name):
    departments = Department.query.filter(
        Department.name.ilike(f"%{name}%")
    ).all()

    if not departments:
        return ERROR_RESPONCE("Department not available", 404)

    result = [{"id": d.id, "name": d.name} for d in departments]
    return SUCCESS_RESPONCE("Department found", result)