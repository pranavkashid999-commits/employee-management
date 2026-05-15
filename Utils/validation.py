def validate_employee(data):
    if not data.get("name"):
        return "name is required"

    if not data.get("email"):
        return "email is required"

    if not data.get("city"):
        return "city is required"

    if not data.get("salary"):
        return "salary is required"

    return None


def validate_department(data):
    if not data.get("name"):
        return "name is required"

    return None