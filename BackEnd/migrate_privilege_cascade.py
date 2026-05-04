"""
Migration script to update foreign key constraint for dashboard_id in privileges
Changes ON DELETE behavior to CASCADE (delete privileges when dashboard is deleted)
"""

from app import create_app
from models import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        try:
            print("="*60)
            print("MIGRATION: PRIVILEGE CASCADE ON DASHBOARD DELETE")
            print("="*60)
            
            # Check database type
            db_url = str(db.engine.url)
            
            if 'sqlite' in db_url.lower():
                print("\n⚠️  SQLite detected - Foreign key constraints cannot be modified")
                print("   SQLite will automatically handle CASCADE based on model definition")
                print("   No migration needed for SQLite")
                
            elif 'mysql' in db_url.lower() or 'mariadb' in db_url.lower():
                print("\nMySQL/MariaDB detected - Updating foreign key constraint...")
                
                # Find the actual constraint name
                print("1. Finding existing foreign key constraint...")
                result = db.session.execute(text('''
                    SELECT CONSTRAINT_NAME 
                    FROM information_schema.KEY_COLUMN_USAGE 
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'privileges' 
                    AND COLUMN_NAME = 'dashboard_id'
                    AND REFERENCED_TABLE_NAME IS NOT NULL
                '''))
                constraint_name = result.scalar()
                
                if constraint_name:
                    print(f"   Found constraint: {constraint_name}")
                    
                    # Drop existing foreign key
                    print("2. Dropping existing foreign key constraint...")
                    db.session.execute(text(f'''
                        ALTER TABLE privileges 
                        DROP FOREIGN KEY {constraint_name}
                    '''))
                    
                    # Add new foreign key with ON DELETE CASCADE
                    print("3. Adding new foreign key with ON DELETE CASCADE...")
                    db.session.execute(text('''
                        ALTER TABLE privileges 
                        ADD CONSTRAINT privileges_ibfk_1 
                        FOREIGN KEY (dashboard_id) 
                        REFERENCES powerbi_dashboards(id) 
                        ON DELETE CASCADE
                    '''))
                    
                    db.session.commit()
                    print("✅ Foreign key constraint updated successfully")
                else:
                    print("⚠️  No foreign key constraint found")
                
            elif 'postgresql' in db_url.lower():
                print("\nPostgreSQL detected - Updating foreign key constraint...")
                
                # Drop existing foreign key
                print("1. Dropping existing foreign key constraint...")
                db.session.execute(text('''
                    ALTER TABLE privileges 
                    DROP CONSTRAINT IF EXISTS privileges_dashboard_id_fkey
                '''))
                
                # Add new foreign key with ON DELETE CASCADE
                print("2. Adding new foreign key with ON DELETE CASCADE...")
                db.session.execute(text('''
                    ALTER TABLE privileges 
                    ADD CONSTRAINT privileges_dashboard_id_fkey 
                    FOREIGN KEY (dashboard_id) 
                    REFERENCES powerbi_dashboards(id) 
                    ON DELETE CASCADE
                '''))
                
                db.session.commit()
                print("✅ Foreign key constraint updated successfully")
                
            else:
                print(f"\n⚠️  Unknown database type: {db_url}")
                print("   Please update the foreign key constraint manually")
            
            print("\n" + "="*60)
            print("MIGRATION COMPLETED")
            print("="*60)
            print("\nNote: When a dashboard is deleted, all its privileges")
            print("      will be automatically deleted in cascade.")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            print("\nNote: If the constraint name is different, you may need to:")
            print("1. Find the actual constraint name:")
            print("   SHOW CREATE TABLE privileges; (MySQL)")
            print("   \\d privileges (PostgreSQL)")
            print("2. Update the constraint name in this script")
            raise

if __name__ == '__main__':
    migrate()
