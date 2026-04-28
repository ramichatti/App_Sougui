from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Role
import base64

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def _require_admin():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return None, (jsonify({'error': 'Admin access required'}), 403)
    return user, None


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (admin only)."""
    try:
        _, err = _require_admin()
        if err:
            return err

        users = User.query.all()
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'role_id': user.role_id,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'profile_image': base64.b64encode(user.profile_image).decode('utf-8') if user.profile_image else None
            })
        return jsonify({'users': users_data}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get users', 'details': str(e)}), 500


@admin_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """Create a new user (admin only)."""
    try:
        _, err = _require_admin()
        if err:
            return err

        data = request.get_json()
        required = ['email', 'password', 'first_name', 'last_name']
        if not all(data.get(f) for f in required):
            return jsonify({'error': 'email, password, first_name and last_name are required'}), 400

        if not data.get('role_id'):
            return jsonify({'error': 'role_id is required'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'User with this email already exists'}), 400

        role = Role.query.get(data['role_id'])
        if not role:
            return jsonify({'error': 'Role not found'}), 404

        profile_image = None
        if data.get('profile_image'):
            try:
                profile_image = base64.b64decode(data['profile_image'])
            except Exception:
                pass

        new_user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role_id=data['role_id'],
            is_active=data.get('is_active', True),
            profile_image=profile_image
        )
        new_user.set_password(data['password'])

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'role': new_user.role,
                'role_id': new_user.role_id,
                'is_active': new_user.is_active
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create user', 'details': str(e)}), 500


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update a user (admin only)."""
    try:
        _, err = _require_admin()
        if err:
            return err

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        if 'email' in data and data['email']:
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                return jsonify({'error': 'Email already in use'}), 400
            user.email = data['email']

        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']

        if 'role_id' in data and data['role_id']:
            role = Role.query.get(data['role_id'])
            if not role:
                return jsonify({'error': 'Role not found'}), 404
            user.role_id = data['role_id']

        if 'is_active' in data:
            user.is_active = data['is_active']

        if 'password' in data and data['password']:
            user.set_password(data['password'])

        if 'profile_image' in data and data['profile_image']:
            try:
                user.profile_image = base64.b64decode(data['profile_image'])
            except Exception:
                pass

        db.session.commit()

        return jsonify({
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'role_id': user.role_id,
                'is_active': user.is_active,
                'profile_image': base64.b64encode(user.profile_image).decode('utf-8') if user.profile_image else None
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update user', 'details': str(e)}), 500


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete a user (admin only)."""
    try:
        current_user, err = _require_admin()
        if err:
            return err

        if user_id == current_user.id:
            return jsonify({'error': 'Cannot delete your own account'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user', 'details': str(e)}), 500


@admin_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    """Return all active roles (admin only) — used to populate role dropdowns."""
    try:
        _, err = _require_admin()
        if err:
            return err
        roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
        return jsonify({'roles': [r.to_dict() for r in roles]}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get roles', 'details': str(e)}), 500
