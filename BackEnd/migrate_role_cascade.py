"""
Migration script to update foreign key constraint for role_id
Changes ON DELETE behavior to SET NULL instead of CASCADE
"""

from app import create_app
from models import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        try:
            print("="*60)
            print("MIGRATION: ROLE CASCADE TO SET NULL")
            print("="*60)
            
            # Check database type
            db_url = str(db.engine.url)
            
            if 'sqlite' in db_url.lower():
                print("\n⚠️  SQLite detected - Foreign key constraints cannot be modified")
                print("   SQLite will automatically set role_id to NULL on role deletion")
                print("   No migration needed for SQLite")
                
            elif 'mysql' in db_url.lower() or 'mariadb' in db_url.lower():
                print("\nMySQL/MariaDB detected - Updating foreign key constraint...")
                
                # Drop existing foreign key
                print("1. Dropping existing foreign key constraint...")
                db.session.execute(text('''
                    ALTER TABLE users 
                    DROP FOREIGN KEY users_ibfk_1
                '''))
                
                # Add new foreign key with ON DELETE SET NULL
                print("2. Adding new foreign key with ON DELETE SET NULL...")
                db.session.execute(text('''
                    ALTER TABLE users 
                    ADD CONSTRAINT users_ibfk_1 
                    FOREIGN KEY (role_id) 
                    REFERENCES roles(id) 
                    ON DELETE SET NULL
                '''))
                
                db.session.commit()
                print("✅ Foreign key constraint updated successfully")
                
            elif 'postgresql' in db_url.lower():
                print("\nPostgreSQL detected - Updating foreign key constraint...")
                
                # Drop existing foreign key
                print("1. Dropping existing foreign key constraint...")
                db.session.execute(text('''
                    ALTER TABLE users 
                    DROP CONSTRAINT IF EXISTS users_role_id_fkey
                '''))
                
                # Add new foreign key with ON DELETE SET NULL
                print("2. Adding new foreign key with ON DELETE SET NULL...")
                db.session.execute(text('''
                    ALTER TABLE users 
                    ADD CONSTRAINT users_role_id_fkey 
                    FOREIGN KEY (role_id) 
                    REFERENCES roles(id) 
                    ON DELETE SET NULL
                '''))
                
                db.session.commit()
                print("✅ Foreign key constraint updated successfully")
                
            else:
                print(f"\n⚠️  Unknown database type: {db_url}")
                print("   Please update the foreign key constraint manually")
            
            print("\n" + "="*60)
            print("MIGRATION COMPLETED")
            print("="*60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            print("\nNote: If the constraint name is different, you may need to:")
            print("1. Find the actual constraint name:")
            print("   SHOW CREATE TABLE users; (MySQL)")
            print("   \\d users (PostgreSQL)")
            print("2. Update the constraint name in this script")
            raise

if __name__ == '__main__':
    migrate()
