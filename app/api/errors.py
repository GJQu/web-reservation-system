from flask import jsonify


class APIError(Exception):
    def __init__(self, message, code, status_code=400):
        self.message = message
        self.code = code
        self.status_code = status_code


class ClassFullError(APIError):
    def __init__(self):
        super().__init__("This class is full", "CLASS_FULL", 409)


class DuplicateReservationError(APIError):
    def __init__(self):
        super().__init__(
            "You already have a reservation for this class",
            "DUPLICATE_RESERVATION",
            409,
        )


class NotFoundError(APIError):
    def __init__(self, resource="Resource"):
        super().__init__(f"{resource} not found", "NOT_FOUND", 404)


class ForbiddenError(APIError):
    def __init__(self):
        super().__init__(
            "You do not have permission to perform this action",
            "FORBIDDEN",
            403,
        )


def register_error_handlers(bp):
    @bp.errorhandler(APIError)
    def handle_api_error(error):
        return jsonify({
            "data": None,
            "error": {
                "code": error.code,
                "message": error.message,
            },
        }), error.status_code

    @bp.errorhandler(401)
    def handle_unauthorized(error):
        return jsonify({
            "data": None,
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Authentication required",
            },
        }), 401
