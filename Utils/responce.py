def SUCCESS_RESPONCE(message, data=None, status_code=200):
    return {
        "status": "success",
        "massage": message,
        "data": data
    }, status_code


def ERROR_RESPONCE(message, error_code, status_code=400):
    return {
        "status": "error",
        "massage": message,
        "error_code": error_code
    }, status_code