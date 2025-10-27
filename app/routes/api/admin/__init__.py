from flask import Blueprint
from app.routes.api.admin.product import api_admin_product_bp
from app.routes.api.admin.category import api_admin_category_bp

api_admin_bp = Blueprint('api_admin', __name__, url_prefix='/admin')
api_admin_bp.register_blueprint(api_admin_product_bp)
api_admin_bp.register_blueprint(api_admin_category_bp)
