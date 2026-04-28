#!/usr/bin/env python
"""List all users in database"""
from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    users = User.query.all()
    
    print("=" * 60)
    print("Users in Database")
    print("=" * 60)
    
    if not users:
        print("❌ No users found!")
        print("\nRun this to create admin user:")
        print("python init_db.py")
    else:
        for user in users:
            print(f"📧 Email: {user.email}")
            print(f"👤 Name: {user.first_name} {user.last_name}")
            print(f"🔑 Role: {user.role}")
            print(f"✅ Active: {user.is_active}")
            print("-" * 60)
    
    print("=" * 60)
