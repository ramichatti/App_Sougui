from app import create_app
from models import db, User, Role, Privilege, PowerBIDashboard


def init_database():
    app = create_app()

    with app.app_context():
        # Disable FK checks so tables drop cleanly regardless of order
        db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 0'))
        db.session.commit()
        db.drop_all()
        db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 1'))
        db.session.commit()
        db.create_all()

        # ── System roles ──────────────────────────────────────────────────────
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

        # ── Sample dashboards ─────────────────────────────────────────────────
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

        # ── Privileges (one per dashboard) ────────────────────────────────────
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

        # ── Assign privileges to roles ────────────────────────────────────────
        # Admin gets all three
        role_admin.privileges.extend([priv_global, priv_vente, priv_achat])
        # Directeur vente gets vente only
        role_vente.privileges.append(priv_vente)
        # Directeur achat gets achat only
        role_achat.privileges.append(priv_achat)

        # ── Default users ─────────────────────────────────────────────────────
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

        print("Database initialized successfully!")
        print("\nRoles created:")
        for r in [role_admin, role_vente, role_achat]:
            print(f"   {r.name} (is_admin={r.is_admin}, privileges={len(r.privileges)})")
        print("\nDashboards created:")
        for d in [dash_global, dash_vente, dash_achat]:
            print(f"   [{d.id}] {d.dashboard_name}")
        print("\nPrivileges created:")
        for p in [priv_global, priv_vente, priv_achat]:
            print(f"   [{p.id}] {p.name} -> dashboard {p.dashboard_id}")
        print("\nDefault users:")
        print("   Admin:            ramichatti14@gmail.com / admin123")
        print("   Directeur Vente:  chattir318@gmail.com   / vente123")
        print("   Directeur Achat:  achat@sougui.com       / achat123")


if __name__ == '__main__':
    init_database()
