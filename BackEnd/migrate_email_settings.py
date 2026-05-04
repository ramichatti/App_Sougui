"""
Script de migration pour créer la table email_settings
"""
from app import create_app
from models import db

def migrate():
    app = create_app()
    
    with app.app_context():
        # Créer la table email_settings
        db.engine.execute("""
            CREATE TABLE IF NOT EXISTS email_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                mail_server VARCHAR(255) NOT NULL,
                mail_port INT NOT NULL,
                mail_use_tls BOOLEAN DEFAULT TRUE,
                mail_username VARCHAR(255) NOT NULL,
                mail_password VARCHAR(255) NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                updated_by INT,
                FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        print("✅ Table email_settings créée avec succès!")

if __name__ == '__main__':
    migrate()
