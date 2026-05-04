from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, AppNotification

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')


@notifications_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id = int(get_jwt_identity())
    notifications = (
        AppNotification.query
        .filter_by(user_id=user_id)
        .order_by(AppNotification.is_read.asc(), AppNotification.created_at.desc())
        .limit(50)
        .all()
    )
    return jsonify([n.to_dict() for n in notifications]), 200


@notifications_bp.route('/<int:notif_id>/read', methods=['PUT'])
@jwt_required()
def mark_read(notif_id):
    user_id = int(get_jwt_identity())
    notif = AppNotification.query.filter_by(id=notif_id, user_id=user_id).first()
    if not notif:
        return jsonify({'error': 'Notification not found'}), 404
    notif.is_read = True
    db.session.commit()
    return jsonify({'message': 'Marked as read'}), 200


@notifications_bp.route('/read-all', methods=['PUT'])
@jwt_required()
def mark_all_read():
    user_id = int(get_jwt_identity())
    AppNotification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'message': 'All notifications marked as read'}), 200
