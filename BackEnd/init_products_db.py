"""
Script pour initialiser les tables de produits et commandes avec des données de test
"""
from app import create_app
from models import db, Produit, Client, Commande, LigneCommande
from datetime import datetime, timedelta
import random

def init_products_database():
    app = create_app()
    
    with app.app_context():
        print("🔄 Création des tables...")
        
        # Créer les tables si elles n'existent pas
        db.create_all()
        print("✅ Tables créées")
        
        # Vérifier si des produits existent déjà
        if Produit.query.first():
            print("⚠️  Des produits existent déjà. Voulez-vous continuer ? (y/n)")
            response = input().lower()
            if response != 'y':
                print("❌ Annulé")
                return
            
            # Supprimer les données existantes
            print("🗑️  Suppression des données existantes...")
            LigneCommande.query.delete()
            Commande.query.delete()
            Client.query.delete()
            Produit.query.delete()
            db.session.commit()
        
        print("\n📦 Création des produits...")
        
        # Catégories de produits artisanaux tunisiens
        categories = {
            'Poterie': [
                ('POT001', 'Vase en céramique bleue', 'Vase traditionnel en céramique de Nabeul avec motifs bleus'),
                ('POT002', 'Assiette décorative', 'Assiette murale en céramique peinte à la main'),
                ('POT003', 'Tajine traditionnel', 'Tajine en terre cuite pour cuisson traditionnelle'),
                ('POT004', 'Bol à couscous', 'Grand bol en céramique pour servir le couscous'),
                ('POT005', 'Plat à poisson', 'Plat ovale en céramique avec motifs marins'),
            ],
            'Textile': [
                ('TEX001', 'Tapis berbère', 'Tapis tissé main avec motifs géométriques berbères'),
                ('TEX002', 'Fouta traditionnelle', 'Serviette de hammam en coton tissé'),
                ('TEX003', 'Chechia rouge', 'Coiffe traditionnelle tunisienne en feutre'),
                ('TEX004', 'Burnous en laine', 'Manteau traditionnel en laine tissée'),
                ('TEX005', 'Couverture Margoum', 'Couverture tissée avec motifs traditionnels'),
            ],
            'Cuir': [
                ('CUI001', 'Babouches brodées', 'Chaussures traditionnelles en cuir brodé'),
                ('CUI002', 'Sac en cuir', 'Sac à main artisanal en cuir tanné'),
                ('CUI003', 'Ceinture berbère', 'Ceinture en cuir avec boucle en argent'),
                ('CUI004', 'Portefeuille gravé', 'Portefeuille en cuir avec gravures traditionnelles'),
                ('CUI005', 'Pouf en cuir', 'Pouf marocain en cuir cousu main'),
            ],
            'Bijoux': [
                ('BIJ001', 'Collier en argent', 'Collier traditionnel en argent avec pendentif'),
                ('BIJ002', 'Bracelet berbère', 'Bracelet en argent avec motifs berbères'),
                ('BIJ003', 'Boucles d\'oreilles', 'Boucles d\'oreilles en argent filigrane'),
                ('BIJ004', 'Bague en corail', 'Bague en argent sertie de corail rouge'),
                ('BIJ005', 'Broche traditionnelle', 'Broche en argent avec émaux colorés'),
            ],
            'Bois': [
                ('BOI001', 'Boîte à bijoux', 'Boîte en bois de thuya sculptée'),
                ('BOI002', 'Plateau de service', 'Plateau en bois d\'olivier gravé'),
                ('BOI003', 'Cadre photo', 'Cadre en bois sculpté avec motifs arabesques'),
                ('BOI004', 'Échiquier artisanal', 'Échiquier en bois incrusté de nacre'),
                ('BOI005', 'Porte-encens', 'Support en bois sculpté pour bâtons d\'encens'),
            ],
            'Verre': [
                ('VER001', 'Verre à thé doré', 'Verre à thé avec dorure traditionnelle'),
                ('VER002', 'Carafe soufflée', 'Carafe en verre soufflé de Carthage'),
                ('VER003', 'Lampe en verre', 'Lampe décorative en verre coloré'),
                ('VER004', 'Bougeoir en verre', 'Bougeoir en verre soufflé multicolore'),
                ('VER005', 'Vase en verre', 'Vase en verre soufflé avec motifs'),
            ]
        }
        
        produits_crees = []
        for categorie, items in categories.items():
            for ref, nom, desc in items:
                prix = round(random.uniform(15.0, 250.0), 2)
                produit = Produit(
                    Produit_Reference=ref,
                    Produit_Nom=nom,
                    Produit_Description=desc,
                    Produit_Categorie=categorie,
                    Produit_PU_HT=prix
                )
                db.session.add(produit)
                produits_crees.append(produit)
        
        db.session.commit()
        print(f"✅ {len(produits_crees)} produits créés")
        
        print("\n👥 Création des clients...")
        clients_data = [
            ('Dupont', 'Jean', 'jean.dupont@email.com', '0612345678', 'Tunis'),
            ('Martin', 'Sophie', 'sophie.martin@email.com', '0623456789', 'Sousse'),
            ('Bernard', 'Pierre', 'pierre.bernard@email.com', '0634567890', 'Sfax'),
            ('Dubois', 'Marie', 'marie.dubois@email.com', '0645678901', 'Bizerte'),
            ('Thomas', 'Luc', 'luc.thomas@email.com', '0656789012', 'Nabeul'),
            ('Robert', 'Claire', 'claire.robert@email.com', '0667890123', 'Hammamet'),
            ('Petit', 'Paul', 'paul.petit@email.com', '0678901234', 'Monastir'),
            ('Durand', 'Julie', 'julie.durand@email.com', '0689012345', 'Kairouan'),
            ('Leroy', 'Marc', 'marc.leroy@email.com', '0690123456', 'Gabès'),
            ('Moreau', 'Anne', 'anne.moreau@email.com', '0601234567', 'Djerba'),
        ]
        
        clients_crees = []
        for nom, prenom, email, tel, ville in clients_data:
            client = Client(
                Client_Nom=nom,
                Client_Prenom=prenom,
                Client_Email=email,
                Client_Telephone=tel,
                Client_Ville=ville,
                Client_Adresse=f'{random.randint(1, 100)} Rue de la République',
                Client_Code_Postal=f'{random.randint(1000, 9999)}'
            )
            db.session.add(client)
            clients_crees.append(client)
        
        db.session.commit()
        print(f"✅ {len(clients_crees)} clients créés")
        
        print("\n📋 Création des commandes et historique de ventes...")
        
        # Créer des commandes sur les 12 derniers mois
        commandes_creees = 0
        lignes_creees = 0
        
        date_debut = datetime.now() - timedelta(days=365)
        
        for i in range(200):  # 200 commandes
            # Date aléatoire dans les 12 derniers mois
            jours_aleatoires = random.randint(0, 365)
            date_commande = date_debut + timedelta(days=jours_aleatoires)
            
            client = random.choice(clients_crees)
            
            commande = Commande(
                Id_Client=client.Id_Client,
                Date_Commande=date_commande,
                Statut_Commande=random.choice(['Livrée', 'En cours', 'Annulée']),
                Montant_Total=0
            )
            db.session.add(commande)
            db.session.flush()  # Pour obtenir l'ID
            
            # Ajouter 1 à 5 produits par commande
            nb_produits = random.randint(1, 5)
            montant_total = 0
            
            produits_commande = random.sample(produits_crees, nb_produits)
            for produit in produits_commande:
                quantite = random.randint(1, 10)
                prix_unitaire = float(produit.Produit_PU_HT)
                montant_ligne = quantite * prix_unitaire
                montant_total += montant_ligne
                
                ligne = LigneCommande(
                    Id_Commande=commande.Id_Commande,
                    Id_Produit=produit.Id_Produit,
                    Quantite=quantite,
                    Prix_Unitaire=prix_unitaire,
                    Montant_Ligne=montant_ligne
                )
                db.session.add(ligne)
                lignes_creees += 1
            
            commande.Montant_Total = montant_total
            commandes_creees += 1
        
        db.session.commit()
        print(f"✅ {commandes_creees} commandes créées")
        print(f"✅ {lignes_creees} lignes de commande créées")
        
        print("\n" + "="*60)
        print("✨ Base de données initialisée avec succès !")
        print("="*60)
        print(f"📦 Produits: {len(produits_crees)}")
        print(f"👥 Clients: {len(clients_crees)}")
        print(f"📋 Commandes: {commandes_creees}")
        print(f"📝 Lignes de commande: {lignes_creees}")
        print("="*60)

if __name__ == '__main__':
    init_products_database()
