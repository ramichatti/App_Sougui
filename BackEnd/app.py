from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from config import Config
from models import db

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
    # Configure CORS to allow credentials
    CORS(app, 
         resources={r"/api/*": {
             "origins": ["http://localhost:4200"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True
         }})
    
    jwt = JWTManager(app)
    mail.init_app(app)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired', 'message': 'Please login again'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token', 'message': str(error)}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization token is required', 'message': str(error)}), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has been revoked'}), 401
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.dashboard import dashboard_bp
    from routes.profile import profile_bp
    from routes.powerbi import powerbi_bp
    from routes.roles import roles_bp
    from routes.notifications import notifications_bp
    from routes.ml_prediction import ml_bp
    from routes.delivery_routes import delivery_bp  # ← AJOUTER CETTE LIGNE
    from routes.email_settings import email_settings_bp  # ← NOUVELLE ROUTE

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(powerbi_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(ml_bp)
    app.register_blueprint(delivery_bp)  # ← AJOUTER CETTE LIGNE
    app.register_blueprint(email_settings_bp)  # ← NOUVELLE ROUTE
    
    # Health check
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok', 'message': 'Sougui API is running'}), 200
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print("Sougui Backend API Starting...")
    print("=" * 60)
    print("API URL: http://localhost:5000/api")
    print("Default Admin: ramichatti14@gmail.com / admin123")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)