from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Role, Privilege, PowerBIDashboard, AppNotification

roles_bp = Blueprint('roles', __name__, url_prefix='/api/roles')


def _require_admin():
    """Return (user, error_response) — error_response is None on success."""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return None, (jsonify({'error': 'Admin access required'}), 403)
    return user, None


# ─── ROLES ───────────────────────────────────────────────────────────────────

@roles_bp.route('', methods=['GET'])
@jwt_required()
def list_roles():
    """List all roles (admin only)."""
    try:
        user, err = _require_admin()
        if err:
            return err
        roles = Role.query.order_by(Role.created_at).all()
        return jsonify({'roles': [r.to_dict(include_privileges=True) for r in roles]}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to list roles', 'details': str(e)}), 500


@roles_bp.route('', methods=['POST'])
@jwt_required()
def create_role():
    """Create a new role (admin only). If is_admin=True, automatically assign all privileges."""
    try:
        user, err = _require_admin()
        if err:
            return err

        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'error': 'Role name is required'}), 400

        if Role.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'A role with that name already exists'}), 400

        is_admin = bool(data.get('is_admin', False))

        role = Role(
            name=data['name'].strip(),
            description=data.get('description', ''),
            is_admin=is_admin,
            is_system=False,
            is_active=bool(data.get('is_active', True))
        )
        db.session.add(role)
        db.session.flush()  # Get role.id before commit

        # If is_admin=True, automatically assign all privileges
        if is_admin:
            all_privileges = Privilege.query.all()
            for privilege in all_privileges:
                if privilege not in role.privileges:
                    role.privileges.append(privilege)
            
            print(f"\n✅ Admin role created: {role.name}")
            print(f"   → Automatically assigned {len(all_privileges)} privilege(s)")

        db.session.commit()
        
        message = 'Role created'
        if is_admin and all_privileges:
            message += f' with {len(all_privileges)} privilege(s) automatically assigned'
        
        return jsonify({
            'message': message,
            'role': role.to_dict(include_privileges=True)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create role', 'details': str(e)}), 500


@roles_bp.route('/<int:role_id>', methods=['PUT'])
@jwt_required()
def update_role(role_id):
    """Update a role (admin only). If is_admin changes to True, assign all privileges."""
    try:
        user, err = _require_admin()
        if err:
            return err

        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': 'Role not found'}), 404

        data = request.get_json()
        
        # Track if is_admin is being changed
        was_admin = role.is_admin
        new_is_admin = bool(data.get('is_admin', role.is_admin)) if 'is_admin' in data else role.is_admin

        if 'name' in data and data['name']:
            existing = Role.query.filter_by(name=data['name']).first()
            if existing and existing.id != role_id:
                return jsonify({'error': 'A role with that name already exists'}), 400
            role.name = data['name'].strip()

        if 'description' in data:
            role.description = data['description']

        if 'is_active' in data:
            role.is_active = bool(data['is_active'])

        # Only allow changing is_admin on non-system roles
        if 'is_admin' in data and not role.is_system:
            role.is_admin = new_is_admin
            
            # If changing from non-admin to admin, assign all privileges
            if not was_admin and new_is_admin:
                all_privileges = Privilege.query.all()
                for privilege in all_privileges:
                    if privilege not in role.privileges:
                        role.privileges.append(privilege)
                
                print(f"\n✅ Role upgraded to admin: {role.name}")
                print(f"   → Automatically assigned {len(all_privileges)} privilege(s)")

        db.session.commit()
        
        message = 'Role updated'
        if not was_admin and new_is_admin:
            all_privileges = Privilege.query.all()
            message += f' and {len(all_privileges)} privilege(s) automatically assigned'
        
        return jsonify({
            'message': message,
            'role': role.to_dict(include_privileges=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update role', 'details': str(e)}), 500


@roles_bp.route('/<int:role_id>', methods=['DELETE'])
@jwt_required()
def delete_role(role_id):
    """Delete a role (admin only, non-system roles only). Unassigns users from this role."""
    try:
        user, err = _require_admin()
        if err:
            return err

        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': 'Role not found'}), 404

        if role.is_system:
            return jsonify({'error': 'System roles cannot be deleted'}), 400

        # Unassign all users with this role (set role_id to NULL)
        users_with_role = User.query.filter_by(role_id=role_id).all()
        user_count = len(users_with_role)
        
        for user_to_update in users_with_role:
            user_to_update.role_id = None

        # Delete the role
        db.session.delete(role)
        db.session.commit()
        
        message = f'Role deleted successfully'
        if user_count > 0:
            message += f' ({user_count} user(s) unassigned from this role)'
        
        return jsonify({'message': message}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete role', 'details': str(e)}), 500


# ─── ROLE ↔ PRIVILEGE ASSIGNMENT ─────────────────────────────────────────────

@roles_bp.route('/<int:role_id>/privileges', methods=['POST'])
@jwt_required()
def assign_privilege(role_id):
    """Assign a privilege to a role (admin only)."""
    try:
        user, err = _require_admin()
        if err:
            return err

        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': 'Role not found'}), 404

        data = request.get_json()
        privilege_id = data.get('privilege_id')
        if not privilege_id:
            return jsonify({'error': 'privilege_id is required'}), 400

        privilege = Privilege.query.get(privilege_id)
        if not privilege:
            return jsonify({'error': 'Privilege not found'}), 404

        newly_added = privilege not in role.privileges
        if newly_added:
            role.privileges.append(privilege)
            db.session.commit()

            # Notify all active users with this role
            affected_users = User.query.filter_by(role_id=role.id, is_active=True).all()
            dashboard_name = privilege.dashboard.dashboard_name if privilege.dashboard else privilege.name
            title = 'Nouveau privilège accordé'
            message = f'Le privilège "{privilege.name}" ({dashboard_name}) a été ajouté à votre rôle {role.name}.'

            for affected_user in affected_users:
                notif = AppNotification(
                    user_id=affected_user.id,
                    title=title,
                    message=message,
                    type='privilege'
                )
                db.session.add(notif)

            db.session.commit()

            # Send emails asynchronously (best-effort)
            from app import mail
            from utils import send_privilege_notification_email
            for affected_user in affected_users:
                send_privilege_notification_email(
                    mail,
                    affected_user.email,
                    f'{affected_user.first_name} {affected_user.last_name}',
                    privilege.name,
                    dashboard_name,
                    role.name
                )

        return jsonify({'message': 'Privilege assigned', 'role': role.to_dict(include_privileges=True)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to assign privilege', 'details': str(e)}), 500


@roles_bp.route('/<int:role_id>/privileges/<int:privilege_id>', methods=['DELETE'])
@jwt_required()
def remove_privilege(role_id, privilege_id):
    """Remove a privilege from a role (admin only)."""
    try:
        user, err = _require_admin()
        if err:
            return err

        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': 'Role not found'}), 404

        privilege = Privilege.query.get(privilege_id)
        if not privilege:
            return jsonify({'error': 'Privilege not found'}), 404

        if privilege in role.privileges:
            role.privileges.remove(privilege)
            db.session.commit()

            # Notify affected users
            affected_users = User.query.filter_by(role_id=role.id, is_active=True).all()
            dashboard_name = privilege.dashboard.dashboard_name if privilege.dashboard else privilege.name
            title = 'Privilège retiré'
            message = f'Le privilège "{privilege.name}" ({dashboard_name}) a été retiré de votre rôle {role.name}.'
            for affected_user in affected_users:
                notif = AppNotification(
                    user_id=affected_user.id,
                    title=title,
                    message=message,
                    type='privilege'
                )
                db.session.add(notif)
            db.session.commit()

        return jsonify({'message': 'Privilege removed', 'role': role.to_dict(include_privileges=True)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to remove privilege', 'details': str(e)}), 500


# ─── PRIVILEGES ──────────────────────────────────────────────────────────────

@roles_bp.route('/privileges', methods=['GET'])
@jwt_required()
def list_privileges():
    """List all privileges (admin only)."""
    try:
        user, err = _require_admin()
        if err:
            return err
        privileges = Privilege.query.order_by(Privilege.created_at).all()
        return jsonify({'privileges': [p.to_dict() for p in privileges]}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to list privileges', 'details': str(e)}), 500


@roles_bp.route('/privileges', methods=['POST'])
@jwt_required()
def create_privilege():
    """Create a privilege linked to a dashboard (admin only)."""
    try:
        user, err = _require_admin()
        if err:
            return err

        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'error': 'Privilege name is required'}), 400

        dashboard_id = data.get('dashboard_id')
        if dashboard_id:
            dashboard = PowerBIDashboard.query.get(dashboard_id)
            if not dashboard:
                return jsonify({'error': 'Dashboard not found'}), 404

        privilege = Privilege(
            name=data['name'].strip(),
            description=data.get('description', ''),
            dashboard_id=dashboard_id
        )
        db.session.add(privilege)
        db.session.commit()
        return jsonify({'message': 'Privilege created', 'privilege': privilege.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create privilege', 'details': str(e)}), 500


@roles_bp.route('/privileges/<int:privilege_id>', methods=['PUT'])
@jwt_required()
def update_privilege(privilege_id):
    """Update a privilege (admin only)."""
    try:
        user, err = _require_admin()
        if err:
            return err

        privilege = Privilege.query.get(privilege_id)
        if not privilege:
            return jsonify({'error': 'Privilege not found'}), 404

        data = request.get_json()

        if 'name' in data and data['name']:
            privilege.name = data['name'].strip()
        if 'description' in data:
            privilege.description = data['description']
        if 'dashboard_id' in data:
            dashboard_id = data['dashboard_id']
            if dashboard_id and not PowerBIDashboard.query.get(dashboard_id):
                return jsonify({'error': 'Dashboard not found'}), 404
            privilege.dashboard_id = dashboard_id

        db.session.commit()
        return jsonify({'message': 'Privilege updated', 'privilege': privilege.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update privilege', 'details': str(e)}), 500


@roles_bp.route('/privileges/<int:privilege_id>', methods=['DELETE'])
@jwt_required()
def delete_privilege(privilege_id):
    """Delete a privilege (admin only)."""
    try:
        user, err = _require_admin()
        if err:
            return err

        privilege = Privilege.query.get(privilege_id)
        if not privilege:
            return jsonify({'error': 'Privilege not found'}), 404

        db.session.delete(privilege)
        db.session.commit()
        return jsonify({'message': 'Privilege deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete privilege', 'details': str(e)}), 500
