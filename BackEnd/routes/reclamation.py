from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Reclamation
from datetime import datetime
import base64

reclamation_bp = Blueprint('reclamation', __name__, url_prefix='/api/reclamations')

@reclamation_bp.route('/', methods=['GET'])
@jwt_required()
def get_reclamations():
    """Get reclamations"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.is_admin:
            reclamations = Reclamation.query.all()
        else:
            reclamations = Reclamation.query.filter_by(user_id=current_user_id).all()
        
        reclamations_data = [r.to_dict() for r in reclamations]
        
        return jsonify({'reclamations': reclamations_data}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get reclamations', 'details': str(e)}), 500

@reclamation_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get reclamation statistics"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.is_admin:
            total = Reclamation.query.count()
            new = Reclamation.query.filter_by(status='nouvelle').count()
            in_progress = Reclamation.query.filter_by(status='en_cours').count()
            resolved = Reclamation.query.filter_by(status='resolue').count()
            closed = Reclamation.query.filter_by(status='fermee').count()
        else:
            total = Reclamation.query.filter_by(user_id=current_user_id).count()
            new = Reclamation.query.filter_by(user_id=current_user_id, status='nouvelle').count()
            in_progress = Reclamation.query.filter_by(user_id=current_user_id, status='en_cours').count()
            resolved = Reclamation.query.filter_by(user_id=current_user_id, status='resolue').count()
            closed = Reclamation.query.filter_by(user_id=current_user_id, status='fermee').count()
        
        return jsonify({
            'total': total,
            'new': new,
            'in_progress': in_progress,
            'resolved': resolved,
            'closed': closed
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get stats', 'details': str(e)}), 500

@reclamation_bp.route('/', methods=['POST'])
@jwt_required()
def create_reclamation():
    """Create a new reclamation"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data.get('title') or not data.get('description') or not data.get('category'):
            return jsonify({'error': 'Title, description, and category are required'}), 400
        
        new_reclamation = Reclamation(
            user_id=current_user_id,
            title=data['title'],
            description=data['description'],
            category=data['category'],
            priority=data.get('priority', 'moyenne'),
            admin_notified=False
        )
        
        # Handle attachment if provided
        if data.get('attachment'):
            try:
                attachment_data = data['attachment'].split(',')[1] if ',' in data['attachment'] else data['attachment']
                new_reclamation.attachment = base64.b64decode(attachment_data)
                new_reclamation.attachment_name = data.get('attachment_name', 'attachment')
                new_reclamation.attachment_type = data.get('attachment_type', 'application/octet-stream')
            except Exception as e:
                return jsonify({'error': 'Invalid attachment data', 'details': str(e)}), 400
        
        db.session.add(new_reclamation)
        db.session.commit()
        
        return jsonify({
            'message': 'Reclamation created successfully',
            'reclamation': new_reclamation.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create reclamation', 'details': str(e)}), 500

@reclamation_bp.route('/<int:reclamation_id>', methods=['PUT'])
@jwt_required()
def update_reclamation(reclamation_id):
    """Update a reclamation"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        reclamation = Reclamation.query.get(reclamation_id)
        if not reclamation:
            return jsonify({'error': 'Reclamation not found'}), 404
        
        data = request.get_json()
        
        # Admin can update status and response
        if user.is_admin:
            if 'status' in data:
                reclamation.status = data['status']
                if data['status'] in ['resolue', 'fermee']:
                    reclamation.resolved_at = datetime.utcnow()
            if 'response' in data:
                reclamation.response = data['response']

        # User can update their own reclamation
        elif reclamation.user_id == current_user_id:
            if 'title' in data:
                reclamation.title = data['title']
            if 'description' in data:
                reclamation.description = data['description']
            if 'category' in data:
                reclamation.category = data['category']
            if 'priority' in data:
                reclamation.priority = data['priority']
        else:
            return jsonify({'error': 'Access denied'}), 403
        
        db.session.commit()
        
        return jsonify({
            'message': 'Reclamation updated successfully',
            'reclamation': reclamation.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update reclamation', 'details': str(e)}), 500

@reclamation_bp.route('/<int:reclamation_id>', methods=['DELETE'])
@jwt_required()
def delete_reclamation(reclamation_id):
    """Delete a reclamation"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        reclamation = Reclamation.query.get(reclamation_id)
        if not reclamation:
            return jsonify({'error': 'Reclamation not found'}), 404
        
        if not user.is_admin and reclamation.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        db.session.delete(reclamation)
        db.session.commit()
        
        return jsonify({'message': 'Reclamation deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete reclamation', 'details': str(e)}), 500

@reclamation_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get count of unread reclamations for admin"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_admin:
            return jsonify({'count': 0}), 200
        
        # Count reclamations that are new and not yet notified
        count = Reclamation.query.filter_by(status='nouvelle', admin_notified=False).count()
        
        return jsonify({'count': count}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get unread count', 'details': str(e)}), 500

@reclamation_bp.route('/mark-notified', methods=['POST'])
@jwt_required()
def mark_notified():
    """Mark reclamations as notified for admin"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        reclamation_ids = data.get('ids', [])
        
        if reclamation_ids:
            Reclamation.query.filter(Reclamation.id.in_(reclamation_ids)).update(
                {Reclamation.admin_notified: True}, 
                synchronize_session=False
            )
        else:
            # Mark all new reclamations as notified
            Reclamation.query.filter_by(status='nouvelle', admin_notified=False).update(
                {Reclamation.admin_notified: True}
            )
        
        db.session.commit()
        
        return jsonify({'message': 'Marked as notified'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to mark as notified', 'details': str(e)}), 500

@reclamation_bp.route('/<int:reclamation_id>/attachment', methods=['GET'])
@jwt_required()
def get_attachment(reclamation_id):
    """Get reclamation attachment"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        reclamation = Reclamation.query.get(reclamation_id)
        if not reclamation:
            return jsonify({'error': 'Reclamation not found'}), 404
        
        # Check access rights
        if not user.is_admin and reclamation.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        if not reclamation.attachment:
            return jsonify({'error': 'No attachment found'}), 404
        
        attachment_base64 = base64.b64encode(reclamation.attachment).decode('utf-8')
        
        return jsonify({
            'attachment': attachment_base64,
            'name': reclamation.attachment_name,
            'type': reclamation.attachment_type
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get attachment', 'details': str(e)}), 500
