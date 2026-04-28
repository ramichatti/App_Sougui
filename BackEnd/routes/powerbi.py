from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, PowerBIDashboard, Privilege, User

powerbi_bp = Blueprint('powerbi', __name__, url_prefix='/api/powerbi')


def _get_user():
    current_user_id = int(get_jwt_identity())
    return User.query.get(current_user_id)


@powerbi_bp.route('/dashboards', methods=['GET'])
@jwt_required()
def get_dashboards():
    """Return active dashboards the current user has access to via their role's privileges."""
    try:
        user = _get_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if user.is_admin:
            # Admin sees all active dashboards
            dashboards = PowerBIDashboard.query.filter_by(is_active=True).all()
        else:
            dashboard_ids = user.get_accessible_dashboard_ids()
            dashboards = PowerBIDashboard.query.filter(
                PowerBIDashboard.id.in_(dashboard_ids),
                PowerBIDashboard.is_active == True
            ).all()

        return jsonify({'dashboards': [d.to_dict() for d in dashboards]}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get dashboards', 'details': str(e)}), 500


@powerbi_bp.route('/dashboards/all', methods=['GET'])
@jwt_required()
def get_all_dashboards():
    """Get all dashboards (admin only)."""
    try:
        user = _get_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403

        dashboards = PowerBIDashboard.query.order_by(PowerBIDashboard.created_at).all()
        return jsonify({'dashboards': [d.to_dict() for d in dashboards]}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get dashboards', 'details': str(e)}), 500


@powerbi_bp.route('/dashboards', methods=['POST'])
@jwt_required()
def create_dashboard():
    """Create a dashboard and automatically create a matching privilege (admin only)."""
    try:
        user = _get_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json()
        if not data.get('dashboard_name') or not data.get('embed_url'):
            return jsonify({'error': 'dashboard_name and embed_url are required'}), 400

        dashboard = PowerBIDashboard(
            dashboard_name=data['dashboard_name'],
            embed_url=data['embed_url'],
            description=data.get('description'),
            is_active=data.get('is_active', True)
        )
        db.session.add(dashboard)
        db.session.flush()  # get dashboard.id before commit

        # Auto-create a privilege for this dashboard
        privilege = Privilege(
            name=f"Voir {dashboard.dashboard_name}",
            description=f"Accès au tableau de bord : {dashboard.dashboard_name}",
            dashboard_id=dashboard.id
        )
        db.session.add(privilege)
        db.session.commit()

        return jsonify({
            'message': 'Dashboard created successfully',
            'dashboard': dashboard.to_dict(),
            'privilege': privilege.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create dashboard', 'details': str(e)}), 500


@powerbi_bp.route('/dashboards/<int:dashboard_id>', methods=['PUT'])
@jwt_required()
def update_dashboard(dashboard_id):
    """Update a dashboard (admin only)."""
    try:
        user = _get_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403

        dashboard = PowerBIDashboard.query.get(dashboard_id)
        if not dashboard:
            return jsonify({'error': 'Dashboard not found'}), 404

        data = request.get_json()
        if 'dashboard_name' in data:
            dashboard.dashboard_name = data['dashboard_name']
        if 'embed_url' in data:
            dashboard.embed_url = data['embed_url']
        if 'description' in data:
            dashboard.description = data['description']
        if 'is_active' in data:
            dashboard.is_active = data['is_active']

        db.session.commit()
        return jsonify({'message': 'Dashboard updated successfully', 'dashboard': dashboard.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update dashboard', 'details': str(e)}), 500


@powerbi_bp.route('/dashboards/<int:dashboard_id>', methods=['DELETE'])
@jwt_required()
def delete_dashboard(dashboard_id):
    """Delete a dashboard and its linked privileges (admin only)."""
    try:
        user = _get_user()
        if not user or not user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403

        dashboard = PowerBIDashboard.query.get(dashboard_id)
        if not dashboard:
            return jsonify({'error': 'Dashboard not found'}), 404

        db.session.delete(dashboard)
        db.session.commit()
        return jsonify({'message': 'Dashboard deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete dashboard', 'details': str(e)}), 500
