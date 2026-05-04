from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, PowerBIDashboard, Privilege

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


@dashboard_bp.route('/<int:dashboard_id>/users', methods=['GET'])
@jwt_required()
def get_dashboard_users(dashboard_id):
    """Return all users who have access to a specific dashboard."""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)

        if not current_user:
            return jsonify({'error': 'User not found'}), 404

        # Check if dashboard exists
        dashboard = PowerBIDashboard.query.get(dashboard_id)
        if not dashboard:
            return jsonify({'error': 'Dashboard not found'}), 404

        # Get all privileges linked to this dashboard
        privileges = Privilege.query.filter_by(dashboard_id=dashboard_id).all()
        
        # Get all roles that have these privileges
        role_ids = set()
        for privilege in privileges:
            for role in privilege.roles:
                if role.is_active:
                    role_ids.add(role.id)

        # Get all active users with these roles
        users_with_access = []
        
        # Add all admins
        import base64
        admin_users = User.query.filter_by(is_active=True).all()
        for user in admin_users:
            if user.is_admin:
                profile_image = None
                if user.profile_image:
                    profile_image = base64.b64encode(user.profile_image).decode('utf-8')
                
                users_with_access.append({
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'role': user.role,
                    'is_admin': True,
                    'profile_image': profile_image
                })

        # Add users with specific roles
        if role_ids:
            role_users = User.query.filter(
                User.role_id.in_(role_ids),
                User.is_active == True
            ).all()
            
            for user in role_users:
                if not user.is_admin:  # Don't duplicate admins
                    profile_image = None
                    if user.profile_image:
                        profile_image = base64.b64encode(user.profile_image).decode('utf-8')
                    
                    users_with_access.append({
                        'id': user.id,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'role': user.role,
                        'is_admin': False,
                        'profile_image': profile_image
                    })

        # Remove duplicates based on user id
        seen_ids = set()
        unique_users = []
        for user in users_with_access:
            if user['id'] not in seen_ids:
                seen_ids.add(user['id'])
                unique_users.append(user)

        return jsonify({
            'users': unique_users,
            'total': len(unique_users)
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get dashboard users', 'details': str(e)}), 500
