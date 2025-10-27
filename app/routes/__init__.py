from flask import redirect, url_for, Blueprint, render_template, request, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request, unset_jwt_cookies

home_bp = Blueprint('home', __name__)

@home_bp.route('/', methods=['GET'])
@jwt_required(optional=True)
def index():
    try:
        # Try to verify JWT without raising exception
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        claims = get_jwt()

        if identity:
            user_id = identity.get("id") if isinstance(identity, dict) else identity
            is_admin = claims.get("is_admin")

            if is_admin:
                return redirect(url_for('admin.index'))
            return redirect(url_for('user.index'))
    except:
        # Clear expired cookies
        response = make_response(render_template('home/index.html'))
        unset_jwt_cookies(response)
        return response
    
    return render_template('home/index.html')