"""
Modèle de Classification des Fournisseurs - Iyadh
Classifie les fournisseurs en trois segments : En Risque, Standard, Clé
basé sur leur historique d'achats
"""
import pandas as pd
import numpy as np
import pyodbc
import pickle
import joblib
import os
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration DWH
SQL_SERVER = os.getenv('DWH_SERVER', 'localhost,1433')
SQL_DATABASE = os.getenv('DWH_DATABASE', 'Sougui_DWH')
SQL_USER = os.getenv('DWH_USER', 'sa')
SQL_PASSWORD = os.getenv('DWH_PASSWORD', 'admin')

def get_dwh_connection():
    """Connexion au Data Warehouse"""
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        f"UID={SQL_USER};"
        f"PWD={SQL_PASSWORD};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def extract_supplier_features():
    """
    Extrait les features des fournisseurs depuis le DWH
    """
    print("=" * 70)
    print("EXTRACTION DES DONNÉES FOURNISSEURS")
    print("=" * 70)
    
    conn = get_dwh_connection()
    
    # Requête pour extraire les features des fournisseurs
    query = """
        SELECT 
            f.id_fournisseur,
            f.nom_fournisseur,
            f.matricule_fiscal,
            f.telephone,
            
            -- Métriques d'achat
            COUNT(DISTINCT fa.num_facture) as nb_factures,
            COUNT(DISTINCT fa.id_produit) as nb_produits_differents,
            SUM(fa.quantite) as quantite_totale,
            AVG(fa.quantite) as quantite_moyenne,
            
            -- Métriques financières
            SUM(fa.montant_ht_facture) as montant_total_ht,
            AVG(fa.montant_ht_facture) as montant_moyen_ht,
            SUM(fa.montant_ttc_facture) as montant_total_ttc,
            SUM(fa.reste_du) as total_reste_du,
            
            -- Taux de paiement
            CASE 
                WHEN SUM(fa.montant_ttc_facture) > 0 
                THEN (SUM(fa.montant_ttc_facture) - SUM(fa.reste_du)) / SUM(fa.montant_ttc_facture)
                ELSE 0 
            END as taux_paiement,
            
            -- Régularité (nombre de mois distincts avec achats)
            COUNT(DISTINCT d.Annee * 100 + d.Mois) as nb_mois_actifs,
            
            -- Récence (jours depuis dernier achat)
            DATEDIFF(DAY, MAX(d.Full_Date), GETDATE()) as jours_depuis_dernier_achat,
            
            -- Montant moyen par ligne
            AVG(fa.montant_ligne) as montant_moyen_ligne,
            
            -- Variabilité des montants (écart-type)
            STDEV(fa.montant_ht_facture) as ecart_type_montant
            
        FROM dbo.Dim_Fournisseur f
        LEFT JOIN dbo.Fact_Achat fa ON f.id_fournisseur = fa.id_fournisseur
        LEFT JOIN dbo.Dim_Date d ON fa.date_key = d.Date_Key
        GROUP BY f.id_fournisseur, f.nom_fournisseur, f.matricule_fiscal, f.telephone
        HAVING COUNT(DISTINCT fa.num_facture) > 0
    """
    
    print("Exécution de la requête...")
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"✅ {len(df)} fournisseurs extraits")
    print(f"\nAperçu des données:")
    print(df.head())
    print(f"\nStatistiques:")
    print(df.describe())
    
    return df

def create_segments(df):
    """
    Crée les segments fournisseurs sur trois classes :
    0 = En Risque, 1 = Standard, 2 = Clé
    """
    print("\n" + "=" * 70)
    print("CRÉATION DES SEGMENTS")
    print("=" * 70)
    
    # Calculer les seuils de distribution
    median_montant = df['montant_total_ht'].median()
    if not median_montant or median_montant == 0:
        median_montant = 1.0
    
    # Score composite inspiré de la logique de segmentation backend
    df['score'] = 0.0
    df['score'] += df['taux_paiement'].clip(0, 1) * 100 * 0.35
    df['score'] += (df['nb_mois_actifs'].clip(0, 12) / 12 * 100) * 0.25
    df['score'] += (100 - df['jours_depuis_dernier_achat'].clip(0, 365) / 365 * 100) * 0.20
    df['score'] += (df['montant_total_ht'] / median_montant * 100).clip(0, 100) * 0.20
    
    q33 = df['score'].quantile(0.33)
    q66 = df['score'].quantile(0.66)
    
    # Créer les segments par quantiles pour garantir une répartition plus logique
    df['segment'] = 0
    df.loc[df['score'] >= q33, 'segment'] = 1
    df.loc[df['score'] >= q66, 'segment'] = 2
    
    print(f"Score quantile 33%: {q33:.2f}, 66%: {q66:.2f}")
    print(f"Fournisseurs En Risque: {(df['segment'] == 0).sum()}")
    print(f"Fournisseurs Standard: {(df['segment'] == 1).sum()}")
    print(f"Fournisseurs Clé: {(df['segment'] == 2).sum()}")
    
    return df

def train_model(df):
    """
    Entraîne le modèle Random Forest
    """
    print("\n" + "=" * 70)
    print("ENTRAÎNEMENT DU MODÈLE")
    print("=" * 70)
    
    # Sélectionner les features
    feature_columns = [
        'nb_factures',
        'nb_produits_differents',
        'quantite_totale',
        'quantite_moyenne',
        'montant_total_ht',
        'montant_moyen_ht',
        'total_reste_du',
        'taux_paiement',
        'nb_mois_actifs',
        'jours_depuis_dernier_achat',
        'montant_moyen_ligne'
    ]
    
    # Gérer les valeurs manquantes
    df[feature_columns] = df[feature_columns].fillna(0)
    
    X = df[feature_columns]
    y = df['segment']
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Normalisation
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Entraînement Random Forest
    print("Entraînement du Random Forest...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Évaluation
    y_pred = model.predict(X_test_scaled)
    
    print("\n📊 RÉSULTATS DU MODÈLE:")
    print("\nRapport de Classification:")
    print(classification_report(
        y_test,
        y_pred,
        labels=[0, 1, 2],
        target_names=['En Risque', 'Standard', 'Clé']
    ))
    
    print("\nMatrice de Confusion:")
    print(confusion_matrix(y_test, y_pred, labels=[0, 1, 2]))
    
    accuracy = model.score(X_test_scaled, y_test)
    print(f"\nAccuracy: {accuracy:.3f}")
    
    # Feature importance
    print("\n📈 IMPORTANCE DES FEATURES:")
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.iterrows():
        print(f"  {row['feature']}: {row['importance']:.3f}")
    
    return model, scaler, feature_columns

def save_model(model, scaler, feature_columns):
    """
    Sauvegarde le modèle et les métadonnées
    """
    print("\n" + "=" * 70)
    print("SAUVEGARDE DU MODÈLE")
    print("=" * 70)
    
    # Créer le dossier si nécessaire
    os.makedirs('ml_models/Iyadh', exist_ok=True)
    
    # Sauvegarder le modèle
    model_path = 'ml_models/Iyadh/supplier_classifier.pkl'
    joblib.dump(model, model_path)
    print(f"✅ Modèle sauvegardé: {model_path}")
    
    # Sauvegarder le scaler
    scaler_path = 'ml_models/Iyadh/supplier_scaler.pkl'
    joblib.dump(scaler, scaler_path)
    print(f"✅ Scaler sauvegardé: {scaler_path}")
    
    # Sauvegarder les features
    features_path = 'ml_models/Iyadh/feature_columns.pkl'
    joblib.dump(feature_columns, features_path)
    print(f"✅ Features sauvegardées: {features_path}")
    
    # Sauvegarder les métadonnées
    metadata = {
        'model_type': 'RandomForestClassifier',
        'n_features': len(feature_columns),
        'feature_names': feature_columns,
        'trained_date': datetime.now().isoformat(),
        'description': 'Classification des fournisseurs (En Risque/Standard/Clé)'
    }
    
    metadata_path = 'ml_models/Iyadh/model_metadata.pkl'
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"✅ Métadonnées sauvegardées: {metadata_path}")

def main():
    """
    Pipeline principal d'entraînement
    """
    print("🚀 ENTRAÎNEMENT DU MODÈLE DE CLASSIFICATION DES FOURNISSEURS")
    print("=" * 70)
    
    # 1. Extraction des données
    df = extract_supplier_features()
    
    # 2. Création des segments
    df = create_segments(df)
    
    # 3. Entraînement du modèle
    model, scaler, feature_columns = train_model(df)
    
    # 4. Sauvegarde
    save_model(model, scaler, feature_columns)
    
    print("\n" + "=" * 70)
    print("✅ ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS!")
    print("=" * 70)
    print("\nFichiers générés:")
    print("  - supplier_classifier.pkl")
    print("  - supplier_scaler.pkl")
    print("  - feature_columns.pkl")
    print("  - model_metadata.pkl")

if __name__ == "__main__":
    main()
