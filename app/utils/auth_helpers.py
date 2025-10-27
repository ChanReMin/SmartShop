from flask_jwt_extended import get_jwt_identity
from app.models.user import User

def get_current_user():
    """
    Returns the current logged-in user object or None if not authenticated.
    """
    identity = get_jwt_identity()
    if not identity:
        return None

    # If identity is a dict, get "id"
    if isinstance(identity, dict):
        identity = identity.get("id")

    return User.query.get(identity)
