"""
Migration script to add attachment and notification fields to reclamations table
"""
from app import app
from models import db

def migrate_reclamations():
    """Add new columns to reclamations table"""
    with app.app_context():
        try:
            # Add attachment columns
            db.engine.execute("""
                ALTER TABLE reclamations 
                ADD COLUMN IF NOT EXISTS attachment BYTEA,
                ADD COLUMN IF NOT EXISTS attachment_name VARCHAR(255),
                ADD COLUMN IF NOT EXISTS attachment_type VARCHAR(100),
                ADD COLUMN IF NOT EXISTS admin_notified BOOLEAN DEFAULT FALSE
            """)
            
            print("✅ Migration completed successfully!")
            print("Added columns:")
            print("  - attachment (BYTEA)")
            print("  - attachment_name (VARCHAR(255))")
            print("  - attachment_type (VARCHAR(100))")
            print("  - admin_notified (BOOLEAN)")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            print("\nNote: If columns already exist, this is expected.")

if __name__ == '__main__':
    migrate_reclamations()
