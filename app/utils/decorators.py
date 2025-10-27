from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import jsonify

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Verify JWT validity
        verify_jwt_in_request()

        # Get claims (you can include 'is_admin' when creating the token)
        claims = get_jwt()
        if not claims.get("is_admin", False):
            return jsonify({"msg": "Admin privilege required"}), 403

        # Proceed if admin
        return fn(*args, **kwargs)
    return wrapper
