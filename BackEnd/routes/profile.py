from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User
from utils import generate_reset_code, send_password_change_code_email, send_password_changed_confirmation_email
from datetime import datetime, timedelta
import base64

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')

@profile_bp.route('/', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'role_id': user.role_id,
                'is_admin': user.is_admin,
                'privileges': [p.to_dict() for p in user.get_privileges()],
                'profile_image': base64.b64encode(user.profile_image).decode('utf-8') if user.profile_image else None
            }
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get profile', 'details': str(e)}), 500

@profile_bp.route('/', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if 'first_name' in data:
            user.first_name = data['first_name']
        
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        if 'email' in data:
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != current_user_id:
                return jsonify({'error': 'Email already in use'}), 400
            user.email = data['email']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'role_id': user.role_id,
                'is_admin': user.is_admin,
                'privileges': [p.to_dict() for p in user.get_privileges()],
                'profile_image': base64.b64encode(user.profile_image).decode('utf-8') if user.profile_image else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500

@profile_bp.route('/photo', methods=['PUT'])
@jwt_required()
def update_photo():
    """Update profile photo"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data or 'profile_image' not in data:
            return jsonify({'error': 'Profile image is required'}), 400
        
        try:
            user.profile_image = base64.b64decode(data['profile_image'])
            db.session.commit()
            
            return jsonify({
                'message': 'Profile photo updated successfully',
                'profile_image': data['profile_image']
            }), 200
        except:
            return jsonify({'error': 'Invalid image format'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update photo', 'details': str(e)}), 500

@profile_bp.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change user password (old method - kept for compatibility)"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to change password', 'details': str(e)}), 500

@profile_bp.route('/request-password-change', methods=['POST'])
@jwt_required()
def request_password_change():
    """Send verification code before password change"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate 6-digit code
        code = generate_reset_code()
        
        # Save code with expiration (15 min)
        user.password_change_code = code
        user.password_change_code_expires = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()
        
        # Send email to the user's actual email address
        mail = current_app.extensions.get('mail')
        recipient_email = user.email
        send_password_change_code_email(mail, recipient_email, code, user.first_name)
        
        # Print code in terminal for development
        print("\n" + "="*60)
        print("🔐 PASSWORD CHANGE CODE")
        print("="*60)
        print(f"User: {user.email}")
        print(f"Code: {code}")
        print(f"Expires: {user.password_change_code_expires}")
        print("="*60 + "\n")
        
        return jsonify({
            'message': 'Code sent to your email',
            'debug_code': code  # For development only
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to send code', 'details': str(e)}), 500

@profile_bp.route('/verify-password-change-code', methods=['POST'])
@jwt_required()
def verify_password_change_code():
    """Verify code before allowing password change"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        code = data.get('code')
        
        if not code:
            return jsonify({'error': 'Code is required'}), 400
        
        # Verify code
        if not user.password_change_code:
            return jsonify({'error': 'No code requested'}), 400
            
        if user.password_change_code != code:
            return jsonify({'error': 'Invalid code'}), 400
            
        if user.password_change_code_expires < datetime.utcnow():
            return jsonify({'error': 'Code expired'}), 400
        
        return jsonify({'message': 'Code verified successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to verify code', 'details': str(e)}), 500

@profile_bp.route('/change-password-with-code', methods=['POST'])
@jwt_required()
def change_password_with_code():
    """Change password after code verification"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        code = data.get('code')
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not code or not current_password or not new_password:
            return jsonify({'error': 'Code, current password and new password are required'}), 400
        
        # Verify code again
        if not user.password_change_code or user.password_change_code != code:
            return jsonify({'error': 'Invalid code'}), 400
            
        if user.password_change_code_expires < datetime.utcnow():
            return jsonify({'error': 'Code expired'}), 400
        
        # Verify current password
        if not user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Change password
        user.set_password(new_password)
        user.password_change_code = None
        user.password_change_code_expires = None
        db.session.commit()
        
        # Send confirmation email to the user's actual email address
        mail = current_app.extensions.get('mail')
        recipient_email = user.email
        send_password_changed_confirmation_email(mail, recipient_email, user.first_name)
        
        print("\n" + "="*60)
        print("✅ PASSWORD CHANGED SUCCESSFULLY")
        print("="*60)
        print(f"User: {user.email}")
        print(f"Time: {datetime.utcnow()}")
        print("="*60 + "\n")
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to change password', 'details': str(e)}), 500
