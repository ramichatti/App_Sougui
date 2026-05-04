"""
Migration script to add email change verification fields to User table
Run this script to update the database schema
"""

from app import create_app
from models import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            print("Current columns in users table:", columns)
            
            # Add email_change_code column if it doesn't exist
            if 'email_change_code' not in columns:
                print("Adding email_change_code column...")
                db.session.execute(text('ALTER TABLE users ADD COLUMN email_change_code VARCHAR(6)'))
                print("✓ email_change_code column added")
            else:
                print("✓ email_change_code column already exists")
            
            # Add email_change_code_expires column if it doesn't exist
            if 'email_change_code_expires' not in columns:
                print("Adding email_change_code_expires column...")
                db.session.execute(text('ALTER TABLE users ADD COLUMN email_change_code_expires DATETIME'))
                print("✓ email_change_code_expires column added")
            else:
                print("✓ email_change_code_expires column already exists")
            
            # Add pending_email column if it doesn't exist
            if 'pending_email' not in columns:
                print("Adding pending_email column...")
                db.session.execute(text('ALTER TABLE users ADD COLUMN pending_email VARCHAR(120)'))
                print("✓ pending_email column added")
            else:
                print("✓ pending_email column already exists")
            
            db.session.commit()
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            raise

if __name__ == '__main__':
    print("="*60)
    print("EMAIL CHANGE FIELDS MIGRATION")
    print("="*60)
    migrate()
