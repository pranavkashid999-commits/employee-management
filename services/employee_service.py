from Modules.employee_module import Employee
from Modules.department import Department
from Database.db import db
from Utils.responce import SUCCESS_RESPONCE, ERROR_RESPONCE
from sqlalchemy import func
from Utils.validation import validate_employee

def create_employee(data):
    error = validate_employee(data)
    if error:
        return ERROR_RESPONCE(error, 400)

    dept = Department.query.filter(
        func.lower(Department.name) == data["department"].lower()
    ).first()

    if not dept:
        return ERROR_RESPONCE("Department not found", 400)

    employee = Employee(
        name=data["name"],
        city=data["city"],
        email=data["email"],
        salary=data["salary"],
        department_id=dept.id
    )

    db.session.add(employee)
    db.session.commit()

    return SUCCESS_RESPONCE(
        "Employee created successfully",
        {
            "id": employee.id,
            "name": employee.name,
            "city": employee.city,
            "salary": employee.salary,
            "department": dept.name
        }
    )

def get_all_employees():
    employees = Employee.query.all()
    data = []

    for emp in employees:
        data.append({
            "id": emp.id,
            "name": emp.name,
            "city": emp.city,
            "email": emp.email,
            "salary": emp.salary,
            "department": emp.department.name if emp.department else None
        })

    return SUCCESS_RESPONCE("Employee list", data)

def get_employee_by_id(emp_id):
    emp = Employee.query.get(emp_id)
    if not emp:
        return ERROR_RESPONCE("Employee not found", 404)

    return SUCCESS_RESPONCE(
        "Employee details",
        {
            "id": emp.id,
            "name": emp.name,
            "city": emp.city,
            "email": emp.email,
            "salary": emp.salary,
            "department": emp.department.name if emp.department else None
        }
    )

def update_employee(emp_id, data):
    emp = Employee.query.get(emp_id)
    if not emp:
        return ERROR_RESPONCE("Employee not found", 404)

    if "department" in data:
        dept = Department.query.filter(
            func.lower(Department.name) == data["department"].lower()
        ).first()
        if not dept:
            return ERROR_RESPONCE("Department not found", 400)
        emp.department_id = dept.id

    emp.name = data.get("name", emp.name)
    emp.city = data.get("city", emp.city)
    emp.email = data.get("email", emp.email)
    emp.salary = data.get("salary", emp.salary)

    db.session.commit()
    return SUCCESS_RESPONCE("Employee updated successfully")

def delete_employee(emp_id):
    emp = Employee.query.get(emp_id)
    if not emp:
        return ERROR_RESPONCE("Employee not found", 404)

    db.session.delete(emp)
    db.session.commit()
    return SUCCESS_RESPONCE("Employee deleted successfully")

def get_employees_by_department(dept_name):
    dept = Department.query.filter(
        func.lower(Department.name) == dept_name.lower()
    ).first()

    if not dept:
        return ERROR_RESPONCE("Department not found", 404)

    employees = Employee.query.filter_by(department_id=dept.id).all()
    data = []

    for emp in employees:
        data.append({
            "id": emp.id,
            "name": emp.name,
            "city": emp.city,
            "email": emp.email,
            "salary": emp.salary,
            "department": dept.name
        })

    return SUCCESS_RESPONCE(f"Employees from {dept.name}", data)

def search_employee_by_name(name):
    employees = Employee.query.filter(
        Employee.name.ilike(f"%{name}%")
    ).all()

    if not employees:
        return ERROR_RESPONCE("Employee not available", 404)

    result = []
    for emp in employees:
        result.append({
            "id": emp.id,
            "name": emp.name,
            "email": emp.email,
            "salary": emp.salary
        })

    return SUCCESS_RESPONCE("Employee found", result)

def search_employee_by_city(city):
    employees = Employee.query.filter(
        Employee.city.ilike(f"%{city}%")
    ).all()

    if not employees:
        return ERROR_RESPONCE("No employee found in this city", 404)

    result = []
    for emp in employees:
        result.append({
            "id": emp.id,
            "name": emp.name,
            "city": emp.city,
            "email": emp.email,
            "salary": emp.salary,
            "department": emp.department.name if emp.department else None
        })

    return SUCCESS_RESPONCE(f"Employees from city: {city}", result)


# ✅ NEW — Search by email
def search_employee_by_email(email):
    employees = Employee.query.filter(
        Employee.email.ilike(f"%{email}%")
    ).all()

    if not employees:
        return ERROR_RESPONCE("No employee found with this email", 404)

    result = []
    for emp in employees:
        result.append({
            "id": emp.id,
            "name": emp.name,
            "city": emp.city,
            "email": emp.email,
            "salary": emp.salary,
            "department": emp.department.name if emp.department else None
        })

    return SUCCESS_RESPONCE(f"Employees matching email: {email}", result)