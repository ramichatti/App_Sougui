"""
Routes pour la gestion des paramètres email (Admin uniquement)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, EmailSettings
from datetime import datetime
import os
from dotenv import load_dotenv, set_key
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

email_settings_bp = Blueprint('email_settings', __name__, url_prefix='/api/email-settings')

load_dotenv()

# Handle OPTIONS requests for CORS preflight
@email_settings_bp.route('', methods=['OPTIONS'])
@email_settings_bp.route('/', methods=['OPTIONS'])
@email_settings_bp.route('/test', methods=['OPTIONS'])
@email_settings_bp.route('/history', methods=['OPTIONS'])
def handle_options():
    """Handle CORS preflight requests"""
    return '', 204

@email_settings_bp.route('', methods=['GET'])
@email_settings_bp.route('/', methods=['GET'])
@jwt_required()
def get_email_settings():
    """
    Récupère les paramètres email actuels (masque le mot de passe)
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        # Récupérer depuis la base de données ou .env
        settings = EmailSettings.query.first()
        
        if settings:
            return jsonify({
                'mail_server': settings.mail_server,
                'mail_port': settings.mail_port,
                'mail_use_tls': settings.mail_use_tls,
                'mail_username': settings.mail_username,
                'mail_password': '********' if settings.mail_password else '',
                'is_configured': True,
                'last_updated': settings.updated_at.isoformat() if settings.updated_at else None,
                'updated_by': settings.updated_by_name if hasattr(settings, 'updated_by_name') else None
            }), 200
        else:
            # Fallback sur .env
            return jsonify({
                'mail_server': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
                'mail_port': int(os.getenv('MAIL_PORT', 587)),
                'mail_use_tls': os.getenv('MAIL_USE_TLS', 'True') == 'True',
                'mail_username': os.getenv('MAIL_USERNAME', ''),
                'mail_password': '********' if os.getenv('MAIL_PASSWORD') else '',
                'is_configured': bool(os.getenv('MAIL_USERNAME')),
                'last_updated': None,
                'updated_by': None
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@email_settings_bp.route('/test', methods=['POST'])
@jwt_required()
def test_email_connection():
    """
    Teste la connexion SMTP avec les paramètres fournis
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        data = request.get_json()
        
        mail_server = data.get('mail_server')
        mail_port = data.get('mail_port')
        mail_use_tls = data.get('mail_use_tls', True)
        mail_username = data.get('mail_username')
        mail_password = data.get('mail_password')
        test_recipient = data.get('test_recipient', mail_username)
        
        if not all([mail_server, mail_port, mail_username, mail_password]):
            return jsonify({'error': 'Tous les champs sont requis'}), 400
        
        # Test de connexion SMTP
        try:
            if mail_use_tls:
                server = smtplib.SMTP(mail_server, mail_port, timeout=10)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(mail_server, mail_port, timeout=10)
            
            server.login(mail_username, mail_password)
            
            # Envoyer un email de test
            msg = MIMEMultipart()
            msg['From'] = mail_username
            msg['To'] = test_recipient
            msg['Subject'] = 'Test de Configuration Email - Sougui'
            
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #4CAF50;">✅ Configuration Email Réussie</h2>
                    <p>Ce message confirme que la configuration SMTP a été testée avec succès.</p>
                    <hr>
                    <p><strong>Serveur:</strong> {mail_server}:{mail_port}</p>
                    <p><strong>Utilisateur:</strong> {mail_username}</p>
                    <p><strong>TLS:</strong> {'Activé' if mail_use_tls else 'Désactivé'}</p>
                    <p><strong>Date:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">
                        Cet email a été envoyé automatiquement par le système Sougui.
                    </p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            server.send_message(msg)
            server.quit()
            
            return jsonify({
                'success': True,
                'message': f'Email de test envoyé avec succès à {test_recipient}',
                'details': {
                    'server': mail_server,
                    'port': mail_port,
                    'username': mail_username,
                    'tls': mail_use_tls
                }
            }), 200
            
        except smtplib.SMTPAuthenticationError:
            return jsonify({
                'success': False,
                'error': 'Échec d\'authentification',
                'message': 'Le nom d\'utilisateur ou le mot de passe est incorrect'
            }), 400
            
        except smtplib.SMTPConnectError:
            return jsonify({
                'success': False,
                'error': 'Erreur de connexion',
                'message': f'Impossible de se connecter à {mail_server}:{mail_port}'
            }), 400
            
        except smtplib.SMTPException as e:
            return jsonify({
                'success': False,
                'error': 'Erreur SMTP',
                'message': str(e)
            }), 400
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Erreur inattendue',
                'message': str(e)
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@email_settings_bp.route('', methods=['PUT'])
@email_settings_bp.route('/', methods=['PUT'])
@jwt_required()
def update_email_settings():
    """
    Met à jour les paramètres email (sauvegarde en base et dans .env)
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        data = request.get_json()
        
        mail_server = data.get('mail_server')
        mail_port = data.get('mail_port')
        mail_use_tls = data.get('mail_use_tls', True)
        mail_username = data.get('mail_username')
        mail_password = data.get('mail_password')
        
        if not all([mail_server, mail_port, mail_username]):
            return jsonify({'error': 'Serveur, port et nom d\'utilisateur sont requis'}), 400
        
        # Vérifier si les paramètres existent déjà
        settings = EmailSettings.query.first()
        
        if settings:
            settings.mail_server = mail_server
            settings.mail_port = mail_port
            settings.mail_use_tls = mail_use_tls
            settings.mail_username = mail_username
            if mail_password and mail_password != '********':
                settings.mail_password = mail_password
            settings.updated_at = datetime.utcnow()
            settings.updated_by = current_user_id
        else:
            settings = EmailSettings(
                mail_server=mail_server,
                mail_port=mail_port,
                mail_use_tls=mail_use_tls,
                mail_username=mail_username,
                mail_password=mail_password if mail_password != '********' else '',
                updated_by=current_user_id
            )
            db.session.add(settings)
        
        db.session.commit()
        
        # Mettre à jour le fichier .env
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        
        set_key(env_path, 'MAIL_SERVER', mail_server)
        set_key(env_path, 'MAIL_PORT', str(mail_port))
        set_key(env_path, 'MAIL_USE_TLS', str(mail_use_tls))
        set_key(env_path, 'MAIL_USERNAME', mail_username)
        if mail_password and mail_password != '********':
            set_key(env_path, 'MAIL_PASSWORD', mail_password)
        
        # Recharger les variables d'environnement
        load_dotenv(override=True)
        
        return jsonify({
            'success': True,
            'message': 'Paramètres email mis à jour avec succès',
            'settings': {
                'mail_server': mail_server,
                'mail_port': mail_port,
                'mail_use_tls': mail_use_tls,
                'mail_username': mail_username,
                'updated_at': settings.updated_at.isoformat(),
                'updated_by': f"{user.first_name} {user.last_name}"
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@email_settings_bp.route('/history', methods=['GET'])
@jwt_required()
def get_email_settings_history():
    """
    Récupère l'historique des modifications des paramètres email
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        # TODO: Implémenter une table d'historique si nécessaire
        settings = EmailSettings.query.first()
        
        if settings:
            history = [{
                'action': 'Configuration actuelle',
                'mail_server': settings.mail_server,
                'mail_username': settings.mail_username,
                'updated_at': settings.updated_at.isoformat() if settings.updated_at else None,
                'updated_by': f"{user.first_name} {user.last_name}" if settings.updated_by == current_user_id else 'Admin'
            }]
            
            return jsonify({'history': history}), 200
        
        return jsonify({'history': []}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
