from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, PowerBIDashboard

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@dashboard_bp.route('/my-dashboards', methods=['GET'])
@jwt_required()
def get_my_dashboards():
    """Return active dashboards the current user can access via their role's privileges."""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if user.is_admin:
            dashboards = PowerBIDashboard.query.filter_by(is_active=True).all()
        else:
            dashboard_ids = user.get_accessible_dashboard_ids()
            dashboards = PowerBIDashboard.query.filter(
                PowerBIDashboard.id.in_(dashboard_ids),
                PowerBIDashboard.is_active == True
            ).all()

        return jsonify({
            'dashboards': [d.to_dict() for d in dashboards],
            'user_role': user.role
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get dashboards', 'details': str(e)}), 500
