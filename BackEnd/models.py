from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

# M2M association table: Role <-> Privilege
role_privileges = db.Table('role_privileges',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    db.Column('privilege_id', db.Integer, db.ForeignKey('privileges.id', ondelete='CASCADE'), primary_key=True)
)


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_admin = db.Column(db.Boolean, default=False)   # grants full admin access
    is_system = db.Column(db.Boolean, default=False)  # built-in, cannot be deleted
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    privileges = db.relationship('Privilege', secondary=role_privileges, backref='roles', lazy='select')

    def to_dict(self, include_privileges=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_admin': self.is_admin,
            'is_system': self.is_system,
            'is_active': self.is_active,
            'privilege_count': len(self.privileges),
            'user_count': len(self.users),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_privileges:
            data['privileges'] = [p.to_dict() for p in self.privileges]
        return data


class PowerBIDashboard(db.Model):
    __tablename__ = 'powerbi_dashboards'

    id = db.Column(db.Integer, primary_key=True)
    dashboard_name = db.Column(db.String(200), nullable=False)
    embed_url = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'dashboard_name': self.dashboard_name,
            'embed_url': self.embed_url,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Privilege(db.Model):
    __tablename__ = 'privileges'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    dashboard_id = db.Column(db.Integer, db.ForeignKey('powerbi_dashboards.id', ondelete='CASCADE'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    dashboard = db.relationship('PowerBIDashboard', backref='privileges')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'dashboard_id': self.dashboard_id,
            'dashboard_name': self.dashboard.dashboard_name if self.dashboard else None,
            'dashboard_is_active': self.dashboard.is_active if self.dashboard else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='SET NULL'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    profile_image = db.Column(db.LargeBinary, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reset_code = db.Column(db.String(6), nullable=True)
    reset_code_expires = db.Column(db.DateTime, nullable=True)

    password_change_code = db.Column(db.String(6), nullable=True)
    password_change_code_expires = db.Column(db.DateTime, nullable=True)

    email_change_code = db.Column(db.String(6), nullable=True)
    email_change_code_expires = db.Column(db.DateTime, nullable=True)
    pending_email = db.Column(db.String(120), nullable=True)

    role_rel = db.relationship('Role', backref='users')

    @property
    def role(self):
        return self.role_rel.name if self.role_rel else None

    @property
    def is_admin(self):
        return self.role_rel.is_admin if self.role_rel else False

    def get_privileges(self):
        if self.role_rel:
            return list(self.role_rel.privileges)
        return []

    def get_accessible_dashboard_ids(self):
        return [p.dashboard_id for p in self.get_privileges() if p.dashboard_id is not None]

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self, include_image=False, include_privileges=False):
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'role_id': self.role_id,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'has_image': self.profile_image is not None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_image and self.profile_image:
            import base64
            data['profile_image'] = base64.b64encode(self.profile_image).decode('utf-8')
        if include_privileges:
            data['privileges'] = [p.to_dict() for p in self.get_privileges()]
        return data


class AppNotification(db.Model):
    __tablename__ = 'app_notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='privilege')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============================================================================
# Modèles pour le système de gestion des produits et commandes
# ============================================================================

class Produit(db.Model):
    __tablename__ = 'dim_produit'
    # Schema removed for MySQL compatibility

    Id_Produit = db.Column(db.Integer, primary_key=True)
    Produit_Reference = db.Column(db.String(100))
    Produit_Nom = db.Column(db.String(255))
    Produit_Description = db.Column(db.String(500))
    Produit_Categorie = db.Column(db.String(100))
    Produit_PU_HT = db.Column(db.Numeric(10, 2))

    def to_dict(self):
        return {
            'Id_Produit': self.Id_Produit,
            'Produit_Reference': self.Produit_Reference or '',
            'Produit_Nom': self.Produit_Nom or '',
            'Produit_Description': self.Produit_Description or '',
            'Produit_Categorie': self.Produit_Categorie or '',
            'Produit_PU_HT': float(self.Produit_PU_HT) if self.Produit_PU_HT else 0.0
        }


class Client(db.Model):
    __tablename__ = 'dim_client'
    # Schema removed for MySQL compatibility

    Id_Client = db.Column(db.Integer, primary_key=True)
    Client_Nom = db.Column(db.String(255))
    Client_Prenom = db.Column(db.String(255))
    Client_Email = db.Column(db.String(255))
    Client_Telephone = db.Column(db.String(50))
    Client_Adresse = db.Column(db.String(500))
    Client_Ville = db.Column(db.String(100))
    Client_Code_Postal = db.Column(db.String(20))

    def to_dict(self):
        return {
            'Id_Client': self.Id_Client,
            'Client_Nom': self.Client_Nom or '',
            'Client_Prenom': self.Client_Prenom or '',
            'Client_Email': self.Client_Email or '',
            'Client_Telephone': self.Client_Telephone or '',
            'Client_Adresse': self.Client_Adresse or '',
            'Client_Ville': self.Client_Ville or '',
            'Client_Code_Postal': self.Client_Code_Postal or ''
        }


class Commande(db.Model):
    __tablename__ = 'fact_commande'
    # Schema removed for MySQL compatibility

    Id_Commande = db.Column(db.Integer, primary_key=True)
    Id_Client = db.Column(db.Integer, db.ForeignKey('dim_client.Id_Client'))
    Date_Commande = db.Column(db.DateTime)
    Statut_Commande = db.Column(db.String(50))
    Montant_Total = db.Column(db.Numeric(10, 2))

    def to_dict(self):
        return {
            'Id_Commande': self.Id_Commande,
            'Id_Client': self.Id_Client,
            'Date_Commande': self.Date_Commande.isoformat() if self.Date_Commande else None,
            'Statut_Commande': self.Statut_Commande or '',
            'Montant_Total': float(self.Montant_Total) if self.Montant_Total else 0.0
        }


class LigneCommande(db.Model):
    __tablename__ = 'fact_ligne_commande'
    # Schema removed for MySQL compatibility

    Id_Ligne = db.Column(db.Integer, primary_key=True)
    Id_Commande = db.Column(db.Integer, db.ForeignKey('fact_commande.Id_Commande'))
    Id_Produit = db.Column(db.Integer, db.ForeignKey('dim_produit.Id_Produit'))
    Quantite = db.Column(db.Integer)
    Prix_Unitaire = db.Column(db.Numeric(10, 2))
    Montant_Ligne = db.Column(db.Numeric(10, 2))

    def to_dict(self):
        return {
            'Id_Ligne': self.Id_Ligne,
            'Id_Commande': self.Id_Commande,
            'Id_Produit': self.Id_Produit,
            'Quantite': self.Quantite or 0,
            'Prix_Unitaire': float(self.Prix_Unitaire) if self.Prix_Unitaire else 0.0,
            'Montant_Ligne': float(self.Montant_Ligne) if self.Montant_Ligne else 0.0
        }


# ============================================================================
# Modèle pour les paramètres email (Configuration SMTP)
# ============================================================================

class EmailSettings(db.Model):
    __tablename__ = 'email_settings'

    id = db.Column(db.Integer, primary_key=True)
    mail_server = db.Column(db.String(255), nullable=False)
    mail_port = db.Column(db.Integer, nullable=False)
    mail_use_tls = db.Column(db.Boolean, default=True)
    mail_username = db.Column(db.String(255), nullable=False)
    mail_password = db.Column(db.String(255), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    updater = db.relationship('User', backref='email_settings_updates', foreign_keys=[updated_by])

    @property
    def updated_by_name(self):
        if self.updater:
            return f"{self.updater.first_name} {self.updater.last_name}"
        return None

    def to_dict(self, mask_password=True):
        return {
            'id': self.id,
            'mail_server': self.mail_server,
            'mail_port': self.mail_port,
            'mail_use_tls': self.mail_use_tls,
            'mail_username': self.mail_username,
            'mail_password': '********' if mask_password else self.mail_password,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by,
            'updated_by_name': self.updated_by_name
        }
