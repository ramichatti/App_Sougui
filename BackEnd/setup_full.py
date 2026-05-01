"""
============================================================
Sougui — Full Database Setup (create DB + tables + seed data)
============================================================
This script does everything in one shot:
  1. Creates the MySQL database 'sougui_db' if it doesn't exist
  2. Creates all tables via SQLAlchemy
  3. Seeds roles, dashboards, privileges, role↔privilege mappings, and users

Usage:
    python setup_full.py

Prerequisites:
    - XAMPP running with MySQL on port 3306
    - Python venv activated with requirements.txt installed
"""

import sys
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'sougui_db')


def step1_create_database():
    """Create the MySQL database if it doesn't exist."""
    print("\n" + "=" * 60)
    print("STEP 1 — Creating MySQL database")
    print("=" * 60)

    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        connection.commit()
        connection.close()
        print(f"  ✅ Database '{DB_NAME}' ready")
        return True
    except pymysql.Error as e:
        print(f"  ❌ MySQL error: {e}")
        print("  ⚠️  Make sure XAMPP is running and MySQL is started on port 3306")
        return False


def step2_init_tables_and_seed():
    """Drop/recreate all tables and insert seed data."""
    print("\n" + "=" * 60)
    print("STEP 2 — Creating tables & seeding data")
    print("=" * 60)

    # Import Flask app to get the SQLAlchemy context
    from app import create_app
    from models import db, User, Role, Privilege, PowerBIDashboard

    app = create_app()

    with app.app_context():
        # Clean slate
        db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 0'))
        db.session.commit()
        db.drop_all()
        db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 1'))
        db.session.commit()
        db.create_all()
        print("  ✅ All tables created")

        # ── Roles ────────────────────────────────────────────────────────
        role_admin = Role(
            name='admin',
            description='Administrateur système — accès complet',
            is_admin=True,
            is_system=True,
            is_active=True
        )
        role_vente = Role(
            name='directeur_vente',
            description='Directeur des ventes',
            is_admin=False,
            is_system=True,
            is_active=True
        )
        role_achat = Role(
            name='directeur_achat',
            description='Directeur des achats',
            is_admin=False,
            is_system=True,
            is_active=True
        )
        db.session.add_all([role_admin, role_vente, role_achat])
        db.session.flush()
        print("  ✅ 3 roles created")

        # ── Dashboards ──────────────────────────────────────────────────
        dash_global = PowerBIDashboard(
            dashboard_name='Dashboard Admin — Vue Globale',
            embed_url='https://app.powerbi.com/view?r=YOUR_ADMIN_REPORT_ID',
            description="Vue d'ensemble complète de l'entreprise",
            is_active=True
        )
        dash_vente = PowerBIDashboard(
            dashboard_name='Dashboard Ventes',
            embed_url='https://app.powerbi.com/view?r=YOUR_SALES_REPORT_ID',
            description='Analyse des ventes et performances commerciales',
            is_active=True
        )
        dash_achat = PowerBIDashboard(
            dashboard_name='Dashboard Achats',
            embed_url='https://app.powerbi.com/view?r=YOUR_PURCHASE_REPORT_ID',
            description='Suivi des achats et gestion des fournisseurs',
            is_active=True
        )
        db.session.add_all([dash_global, dash_vente, dash_achat])
        db.session.flush()
        print("  ✅ 3 dashboards created")

        # ── Privileges ──────────────────────────────────────────────────
        priv_global = Privilege(
            name='Voir Vue Globale',
            description='Accès au dashboard vue globale (admin)',
            dashboard_id=dash_global.id
        )
        priv_vente = Privilege(
            name='Voir Dashboard Ventes',
            description='Accès au dashboard des ventes',
            dashboard_id=dash_vente.id
        )
        priv_achat = Privilege(
            name='Voir Dashboard Achats',
            description='Accès au dashboard des achats',
            dashboard_id=dash_achat.id
        )
        db.session.add_all([priv_global, priv_vente, priv_achat])
        db.session.flush()
        print("  ✅ 3 privileges created")

        # ── Role ↔ Privilege assignments ────────────────────────────────
        role_admin.privileges.extend([priv_global, priv_vente, priv_achat])
        role_vente.privileges.append(priv_vente)
        role_achat.privileges.append(priv_achat)
        print("  ✅ Privileges assigned to roles")

        # ── Users ───────────────────────────────────────────────────────
        admin = User(
            email='ramichatti14@gmail.com',
            first_name='Rami',
            last_name='Chatti',
            role_id=role_admin.id
        )
        admin.set_password('admin123')

        directeur_vente = User(
            email='chattir318@gmail.com',
            first_name='Chatti',
            last_name='Rami',
            role_id=role_vente.id
        )
        directeur_vente.set_password('vente123')

        directeur_achat = User(
            email='achat@sougui.com',
            first_name='Fatima',
            last_name='Trabelsi',
            role_id=role_achat.id
        )
        directeur_achat.set_password('achat123')

        db.session.add_all([admin, directeur_vente, directeur_achat])
        db.session.commit()
        print("  ✅ 3 users created")

        # ── Summary ─────────────────────────────────────────────────────
        print("\n" + "=" * 60)
        print("DATABASE SETUP COMPLETE")
        print("=" * 60)

        print("\n📋 Roles:")
        for r in [role_admin, role_vente, role_achat]:
            print(f"   [{r.id}] {r.name:20s}  is_admin={r.is_admin}  privileges={len(r.privileges)}")

        print("\n📊 Dashboards:")
        for d in [dash_global, dash_vente, dash_achat]:
            print(f"   [{d.id}] {d.dashboard_name}")

        print("\n🔑 Privileges:")
        for p in [priv_global, priv_vente, priv_achat]:
            print(f"   [{p.id}] {p.name} → dashboard #{p.dashboard_id}")

        print("\n🔐 Role → Privilege Mapping:")
        print("   admin           → Vue Globale, Ventes, Achats  (ALL)")
        print("   directeur_vente → Ventes")
        print("   directeur_achat → Achats")

        print("\n👥 Default Users:")
        print("   ┌──────────────────┬──────────────────────────────┬────────────┐")
        print("   │ Role             │ Email                        │ Password   │")
        print("   ├──────────────────┼──────────────────────────────┼────────────┤")
        print("   │ Admin            │ ramichatti14@gmail.com       │ admin123   │")
        print("   │ Directeur Vente  │ chattir318@gmail.com         │ vente123   │")
        print("   │ Directeur Achat  │ achat@sougui.com             │ achat123   │")
        print("   └──────────────────┴──────────────────────────────┴────────────┘")

        print("\n🚀 Next steps:")
        print("   1. Start the backend:  python app.py")
        print("   2. Start the frontend: cd ../FrontEnd && npm start")
        print("   3. Open http://localhost:4200")
        print("=" * 60)


if __name__ == '__main__':
    if not step1_create_database():
        sys.exit(1)

    try:
        step2_init_tables_and_seed()
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
