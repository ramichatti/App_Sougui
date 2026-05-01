from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, Privilege
from utils import generate_reset_code, send_reset_code_email
import random
import string
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({'error': 'Aucun compte associé à cet email'}), 401

        if not user.is_active:
            return jsonify({'error': 'Votre compte a été bloqué par l\'administrateur. Contactez le support.'}), 403

        if not user.check_password(data['password']):
            return jsonify({'error': 'Mot de passe incorrect'}), 401
        
        access_token = create_access_token(identity=str(user.id))

        import base64
        profile_image = base64.b64encode(user.profile_image).decode('utf-8') if user.profile_image else None

        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'role_id': user.role_id,
                'is_admin': user.is_admin,
                'privileges': [p.to_dict() for p in user.get_privileges()],
                'profile_image': profile_image
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset code to the user's registered email"""
    try:
        data = request.get_json()

        if not data or not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400

        user = User.query.filter_by(email=data['email']).first()

        if not user:
            return jsonify({'error': 'Aucun compte associé à cet email'}), 404

        # Generate 6-digit code and set 15-minute expiration
        reset_code = generate_reset_code()
        user.reset_code = reset_code
        user.reset_code_expires = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()

        # Send email to the user's actual email address
        mail = current_app.extensions.get('mail')
        email_sent = send_reset_code_email(mail, user.email, reset_code, user.first_name)

        print("=" * 60)
        print(f"🔐 PASSWORD RESET CODE FOR: {user.email}")
        print(f"📧 Code sent to: {user.email}")
        print(f"🔢 Reset Code: {reset_code}")
        print(f"⏰ Expires in: 15 minutes")
        print(f"✅ Email sent: {email_sent}")
        print("=" * 60)

        if email_sent:
            return jsonify({'message': f'Code de réinitialisation envoyé à {user.email}'}), 200
        else:
            return jsonify({
                'message': 'Code généré (échec envoi email)',
                'debug_code': reset_code
            }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error in forgot_password: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erreur lors de l\'envoi du code', 'details': str(e)}), 500

@auth_bp.route('/verify-reset-code', methods=['POST'])
def verify_reset_code():
    """Verify reset code without changing password"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('code'):
            return jsonify({'error': 'Email and code are required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if code is valid and not expired
        if (not user.reset_code or 
            user.reset_code != data['code'] or 
            not user.reset_code_expires or 
            user.reset_code_expires < datetime.utcnow()):
            return jsonify({'error': 'Invalid or expired reset code'}), 400
        
        return jsonify({'message': 'Code verified successfully'}), 200
        
    except Exception as e:
        print(f"Error in verify_reset_code: {str(e)}")
        return jsonify({'error': 'Failed to verify code', 'details': str(e)}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with code"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('code') or not data.get('new_password'):
            return jsonify({'error': 'Email, code, and new password are required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if code is valid and not expired
        if (not user.reset_code or 
            user.reset_code != data['code'] or 
            not user.reset_code_expires or 
            user.reset_code_expires < datetime.utcnow()):
            return jsonify({'error': 'Invalid or expired reset code'}), 400
        
        # Update password
        user.set_password(data['new_password'])
        user.reset_code = None
        user.reset_code_expires = None
        
        db.session.commit()
        
        return jsonify({'message': 'Password reset successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to reset password', 'details': str(e)}), 500

@auth_bp.route('/verify-password', methods=['POST'])
@jwt_required()
def verify_password():
    """Verify the current user's password (used for admin section security re-check)."""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()
        password = (data or {}).get('password', '')
        if not password:
            return jsonify({'error': 'Password is required'}), 400

        if user.check_password(password):
            return jsonify({'valid': True}), 200

        return jsonify({'valid': False, 'error': 'Mot de passe incorrect'}), 401

    except Exception as e:
        return jsonify({'error': 'Verification failed', 'details': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        import base64
        profile_image = base64.b64encode(user.profile_image).decode('utf-8') if user.profile_image else None
        
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
                'profile_image': profile_image
            }
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get user info', 'details': str(e)}), 500
