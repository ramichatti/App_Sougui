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
    dashboard_id = db.Column(db.Integer, db.ForeignKey('powerbi_dashboards.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    dashboard = db.relationship('PowerBIDashboard', backref='privileges')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'dashboard_id': self.dashboard_id,
            'dashboard_name': self.dashboard.dashboard_name if self.dashboard else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    profile_image = db.Column(db.LargeBinary, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reset_code = db.Column(db.String(6), nullable=True)
    reset_code_expires = db.Column(db.DateTime, nullable=True)

    password_change_code = db.Column(db.String(6), nullable=True)
    password_change_code_expires = db.Column(db.DateTime, nullable=True)

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


class Reclamation(db.Model):
    __tablename__ = 'reclamations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.Enum('technique', 'commercial', 'produit', 'service', 'autre'), nullable=False)
    priority = db.Column(db.Enum('basse', 'moyenne', 'haute', 'urgente'), default='moyenne')
    status = db.Column(db.Enum('nouvelle', 'en_cours', 'resolue', 'fermee'), default='nouvelle')
    response = db.Column(db.Text, nullable=True)
    attachment = db.Column(db.LargeBinary, nullable=True)
    attachment_name = db.Column(db.String(255), nullable=True)
    attachment_type = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    admin_notified = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='reclamations')

    def to_dict(self):
        import base64
        user_image = None
        if self.user.profile_image:
            user_image = base64.b64encode(self.user.profile_image).decode('utf-8')

        attachment_data = None
        if self.attachment:
            attachment_data = base64.b64encode(self.attachment).decode('utf-8')

        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': f"{self.user.first_name} {self.user.last_name}",
            'user_email': self.user.email,
            'user_image': user_image,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'response': self.response,
            'has_attachment': self.attachment is not None,
            'attachment_name': self.attachment_name,
            'attachment_type': self.attachment_type,
            'attachment_data': attachment_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'admin_notified': self.admin_notified
        }
