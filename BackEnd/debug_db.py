#!/usr/bin/env python3
import os
from app import create_app
from models import db, User

# Set environment
os.environ['PYTHONPATH'] = '.'

app = create_app()

with app.app_context():
    try:
        # Check database connection
        print("Testing database connection...")
        db.create_all()
        print("✅ Database connection successful")
        
        # Check users
        users = User.query.all()
        print(f"Users in database: {len(users)}")
        
        if len(users) == 0:
            print("Creating admin user...")
            admin = User(
                email='admin@sougui.com',
                first_name='Admin',
                last_name='Sougui',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created")
        
        # Test password verification
        admin = User.query.filter_by(email='admin@sougui.com').first()
        if admin:
            print(f"Admin user found: {admin.email}")
            print(f"Password check result: {admin.check_password('admin123')}")
        else:
            print("❌ Admin user not found")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()