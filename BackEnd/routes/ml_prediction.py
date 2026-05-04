from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import pickle
import joblib
import numpy as np
import pandas as pd
import pyodbc
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

ml_bp = Blueprint('ml', __name__, url_prefix='/api/ml')

# Configuration SQL Server DWH depuis les variables d'environnement
SQL_SERVER = os.getenv('DWH_SERVER', 'localhost,1433')
SQL_DATABASE = os.getenv('DWH_DATABASE', 'Sougui_DWH')
SQL_USER = os.getenv('DWH_USER', 'sa')
SQL_PASSWORD = os.getenv('DWH_PASSWORD', 'admin')

def get_dwh_connection():
    """
    Crée une connexion au Data Warehouse SQL Server
    """
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        f"UID={SQL_USER};"
        f"PWD={SQL_PASSWORD};"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)


def get_kmeans_model(model):
    """
    Extrait le modèle KMeans d'un éventuel Pipeline sklearn.
    Si le modèle est un Pipeline (ex: StandardScaler + KMeans),
    retourne le Pipeline lui-même (predict/transform fonctionnent).
    Si c'est un KMeans direct, le retourne tel quel.
    """
    if hasattr(model, 'named_steps'):
        # C'est un Pipeline sklearn
        return model
    return model


def get_n_clusters(model):
    """
    Récupère n_clusters d'un modèle KMeans ou Pipeline
    """
    if hasattr(model, 'n_clusters'):
        return model.n_clusters
    elif hasattr(model, 'named_steps'):
        # Pipeline: chercher l'étape KMeans
        for name, step in model.steps:
            if hasattr(step, 'n_clusters'):
                return step.n_clusters
        # Dernière étape par défaut
        last_step = model.steps[-1][1]
        if hasattr(last_step, 'n_clusters'):
            return last_step.n_clusters
    return 0


def get_cluster_distances(model, features):
    """
    Calcule les distances aux centres de clusters.
    Gère le cas Pipeline (transform passe par le scaler) et KMeans direct.
    """
    try:
        if hasattr(model, 'transform'):
            # Pipeline ou KMeans avec transform
            distances = model.transform([features])[0]
            return [float(d) for d in distances]
        elif hasattr(model, 'named_steps'):
            # Pipeline: utiliser le KMeans interne après transformation
            features_scaled = model.named_steps.get('scaler', model.steps[0][1]).transform([features])
            kmeans = model.named_steps.get('kmeans', model.steps[-1][1])
            distances = kmeans.transform(features_scaled)[0]
            return [float(d) for d in distances]
    except Exception:
        pass
    return []


# ============================================================================
# BALKIS - Classification et Clustering
# ============================================================================

@ml_bp.route('/balkis/classify', methods=['POST'])
@jwt_required()
def balkis_classify():
    """
    Classification avec Random Forest (Balkis)
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Charger le modèle avec joblib (compatible sklearn)
        model_path = 'ml_models/Balkis/rf_classifier_prod.pkl'
        model = joblib.load(model_path)
        
        # Préparer les données pour la prédiction
        # Adapter selon les features attendues par le modèle
        features = data.get('features', [])
        
        if not features:
            return jsonify({'error': 'Features manquantes'}), 400
        
        # Faire la prédiction
        prediction = model.predict([features])
        probability = model.predict_proba([features])
        
        return jsonify({
            'prediction': int(prediction[0]),
            'probability': probability[0].tolist(),
            'model': 'Random Forest Classifier',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except FileNotFoundError:
        return jsonify({'error': 'Modèle non trouvé'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/balkis/cluster', methods=['POST'])
@jwt_required()
def balkis_cluster():
    """
    Clustering avec KMeans (Balkis)
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Charger le modèle avec joblib (compatible sklearn Pipeline)
        model_path = 'ml_models/Balkis/kmeans_clustering_prod.pkl'
        model = joblib.load(model_path)
        
        # Préparer les données
        features = data.get('features', [])
        
        if not features:
            return jsonify({'error': 'Features manquantes'}), 400
        
        # Faire la prédiction du cluster
        cluster = model.predict([features])
        
        # Récupérer n_clusters (peut être dans un Pipeline)
        if hasattr(model, 'n_clusters'):
            n_clusters = model.n_clusters
        elif hasattr(model, 'named_steps'):
            kmeans_step = model.named_steps.get('kmeans', model.steps[-1][1])
            n_clusters = kmeans_step.n_clusters
        else:
            n_clusters = len(set(cluster))
        
        return jsonify({
            'cluster': int(cluster[0]),
            'n_clusters': n_clusters,
            'model': 'KMeans Clustering',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except FileNotFoundError:
        return jsonify({'error': 'Modèle non trouvé'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/balkis/client-segmentation', methods=['POST'])
@jwt_required()
def balkis_client_segmentation():
    """
    Segmentation des clients avec KMeans (Balkis)
    Utilise les données du DWH pour segmenter les clients B2C
    
    Features utilisées (7):
    - Recency: Jours depuis la dernière commande
    - Frequency: Nombre de commandes
    - Monetary: Montant total dépensé
    - Panier_Moyen: Montant moyen par commande
    - Quantité_Totale: Quantité totale achetée
    - Taux_Réduction: Taux de réduction moyen
    - Produits_Par_Commande: Nombre moyen de produits par commande
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        client_id = data.get('client_id')
        
        # Charger le modèle avec joblib
        model_path = 'ml_models/Balkis/segmentation_clients.pkl'
        model_data = joblib.load(model_path)
        
        # Extraire les composants du dictionnaire
        if isinstance(model_data, dict):
            model = model_data['model']  # Le modèle KMeans
            scaler = model_data.get('scaler')  # Le StandardScaler
            cluster_names_custom = model_data.get('cluster_names', {})  # Noms personnalisés
            features_list = model_data.get('features', [])  # Liste des features
        else:
            # Si c'est directement un modèle (fallback)
            model = model_data
            scaler = None
            cluster_names_custom = {}
            features_list = []
        
        # Connexion au DWH
        conn = get_dwh_connection()
        cursor = conn.cursor()
        
        if client_id:
            # Segmentation d'un client spécifique
            # Récupérer les stats du client depuis le DWH (B2C uniquement)
            # Utiliser les vrais noms de colonnes des tables
            client_query = """
                SELECT 
                    c.Client_Key,
                    c.Nom,
                    c.Prenom,
                    -- Récence: jours depuis la dernière commande (utiliser Full_Date de Dim_Date)
                    COALESCE(DATEDIFF(DAY, MAX(d.Full_Date), GETDATE()), 9999) AS Recency,
                    -- Fréquence: nombre de commandes distinctes
                    COUNT(DISTINCT f.Numero_de_commande) AS Frequency,
                    -- Montant total dépensé
                    COALESCE(SUM(f.Montant_total_de_la_commande), 0) AS Monetary,
                    -- Panier moyen
                    CASE 
                        WHEN COUNT(DISTINCT f.Numero_de_commande) > 0 
                        THEN COALESCE(SUM(f.Montant_total_de_la_commande), 0) / COUNT(DISTINCT f.Numero_de_commande)
                        ELSE 0 
                    END AS Panier_Moyen,
                    -- Quantité totale (en tenant compte des remboursements)
                    COALESCE(SUM(f.Quantite____Remboursement), 0) AS Quantite_Totale,
                    -- Taux de réduction
                    CASE 
                        WHEN SUM(f.Montant_total_de_la_commande) > 0 
                        THEN COALESCE(SUM(f.Reduction), 0) / SUM(f.Montant_total_de_la_commande)
                        ELSE 0 
                    END AS Taux_Reduction,
                    -- Produits par commande
                    CASE 
                        WHEN COUNT(DISTINCT f.Numero_de_commande) > 0 
                        THEN CAST(SUM(f.Quantite____Remboursement) AS FLOAT) / COUNT(DISTINCT f.Numero_de_commande)
                        ELSE 0 
                    END AS Produits_Par_Commande
                FROM dbo.Dim_Client c
                LEFT JOIN dbo.Fact_Vente_B2C f ON c.Client_Key = f.Client_Key
                LEFT JOIN dbo.Dim_Date d ON f.Date_Key = d.Date_Key
                WHERE c.Client_Key = ?
                GROUP BY c.Client_Key, c.Nom, c.Prenom
            """
            cursor.execute(client_query, (client_id,))
            client_row = cursor.fetchone()
            
            if not client_row:
                cursor.close()
                conn.close()
                return jsonify({'error': 'Client non trouvé'}), 404
            
            # Construire les features (7 features)
            recency = int(client_row[3]) if client_row[3] else 9999
            frequency = int(client_row[4]) if client_row[4] else 0
            monetary = float(client_row[5]) if client_row[5] else 0.0
            panier_moyen = float(client_row[6]) if client_row[6] else 0.0
            quantite_totale = float(client_row[7]) if client_row[7] else 0.0
            taux_reduction = float(client_row[8]) if client_row[8] else 0.0
            produits_par_commande = float(client_row[9]) if client_row[9] else 0.0
            
            # Features pour le modèle KMeans (7 features)
            features = [
                recency,
                frequency,
                monetary,
                panier_moyen,
                quantite_totale,
                taux_reduction,
                produits_par_commande
            ]
            
            # Normaliser les features si un scaler est disponible
            if scaler is not None:
                features_scaled = scaler.transform([features])
                cluster = model.predict(features_scaled)
            else:
                cluster = model.predict([features])
            
            cluster_id = int(cluster[0])
            
            # Utiliser les noms personnalisés du modèle s'ils existent
            if cluster_names_custom:
                segment_name = cluster_names_custom.get(cluster_id, f'Segment {cluster_id}')
            else:
                # Noms par défaut
                segment_names = {
                    0: 'Champions',
                    1: 'Clients Fidèles',
                    2: 'Clients Potentiels',
                    3: 'Clients à Risque',
                    4: 'Clients Perdus'
                }
                segment_name = segment_names.get(cluster_id, f'Segment {cluster_id}')
            
            # Calculer les distances aux centres
            if scaler is not None:
                distances = get_cluster_distances(model, features_scaled[0])
            else:
                distances = get_cluster_distances(model, features)
            
            # Nom complet du client
            client_name = f"{client_row[1]} {client_row[2]}".strip()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'client_id': client_id,
                'client_name': client_name,
                'cluster': cluster_id,
                'segment_name': segment_name,
                'n_clusters': get_n_clusters(model),
                'cluster_distances': distances,
                'features_used': {
                    'recency': recency,
                    'frequency': frequency,
                    'monetary': round(monetary, 2),
                    'panier_moyen': round(panier_moyen, 2),
                    'quantite_totale': quantite_totale,
                    'taux_reduction': round(taux_reduction, 4),
                    'produits_par_commande': round(produits_par_commande, 2)
                },
                'model': 'KMeans Client Segmentation (Balkis)',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            # Segmentation globale de tous les clients B2C
            all_clients_query = """
                SELECT 
                    c.Client_Key,
                    c.Nom,
                    c.Prenom,
                    -- Récence: jours depuis la dernière commande (utiliser Full_Date de Dim_Date)
                    COALESCE(DATEDIFF(DAY, MAX(d.Full_Date), GETDATE()), 9999) AS Recency,
                    -- Fréquence: nombre de commandes distinctes
                    COUNT(DISTINCT f.Numero_de_commande) AS Frequency,
                    -- Montant total dépensé
                    COALESCE(SUM(f.Montant_total_de_la_commande), 0) AS Monetary,
                    -- Panier moyen
                    CASE 
                        WHEN COUNT(DISTINCT f.Numero_de_commande) > 0 
                        THEN COALESCE(SUM(f.Montant_total_de_la_commande), 0) / COUNT(DISTINCT f.Numero_de_commande)
                        ELSE 0 
                    END AS Panier_Moyen,
                    -- Quantité totale (en tenant compte des remboursements)
                    COALESCE(SUM(f.Quantite____Remboursement), 0) AS Quantite_Totale,
                    -- Taux de réduction
                    CASE 
                        WHEN SUM(f.Montant_total_de_la_commande) > 0 
                        THEN COALESCE(SUM(f.Reduction), 0) / SUM(f.Montant_total_de_la_commande)
                        ELSE 0 
                    END AS Taux_Reduction,
                    -- Produits par commande
                    CASE 
                        WHEN COUNT(DISTINCT f.Numero_de_commande) > 0 
                        THEN CAST(SUM(f.Quantite____Remboursement) AS FLOAT) / COUNT(DISTINCT f.Numero_de_commande)
                        ELSE 0 
                    END AS Produits_Par_Commande
                FROM dbo.Dim_Client c
                LEFT JOIN dbo.Fact_Vente_B2C f ON c.Client_Key = f.Client_Key
                LEFT JOIN dbo.Dim_Date d ON f.Date_Key = d.Date_Key
                GROUP BY c.Client_Key, c.Nom, c.Prenom
                HAVING COUNT(DISTINCT f.Numero_de_commande) > 0
            """
            cursor.execute(all_clients_query)
            all_clients = cursor.fetchall()
            
            clients_data = []
            segment_counts = {}
            
            # Utiliser les noms personnalisés du modèle s'ils existent
            if cluster_names_custom:
                segment_names = cluster_names_custom
            else:
                # Noms par défaut
                segment_names = {
                    0: 'Champions',
                    1: 'Clients Fidèles',
                    2: 'Clients Potentiels',
                    3: 'Clients à Risque',
                    4: 'Clients Perdus'
                }
            
            for client_row in all_clients:
                recency = int(client_row[3]) if client_row[3] else 9999
                frequency = int(client_row[4]) if client_row[4] else 0
                monetary = float(client_row[5]) if client_row[5] else 0.0
                panier_moyen = float(client_row[6]) if client_row[6] else 0.0
                quantite_totale = float(client_row[7]) if client_row[7] else 0.0
                taux_reduction = float(client_row[8]) if client_row[8] else 0.0
                produits_par_commande = float(client_row[9]) if client_row[9] else 0.0
                
                features = [
                    recency,
                    frequency,
                    monetary,
                    panier_moyen,
                    quantite_totale,
                    taux_reduction,
                    produits_par_commande
                ]
                
                # Normaliser les features si un scaler est disponible
                if scaler is not None:
                    features_scaled = scaler.transform([features])
                    cluster = model.predict(features_scaled)
                else:
                    cluster = model.predict([features])
                
                cluster_id = int(cluster[0])
                segment_name = segment_names.get(cluster_id, f'Segment {cluster_id}')
                
                client_name = f"{client_row[1]} {client_row[2]}".strip()
                
                clients_data.append({
                    'client_id': client_row[0],
                    'client_name': client_name,
                    'cluster': cluster_id,
                    'segment_name': segment_name,
                    'ca_total': round(monetary, 2),
                    'nb_commandes': frequency,
                    'panier_moyen': round(panier_moyen, 2),
                    'recency': recency
                })
                
                segment_counts[segment_name] = segment_counts.get(segment_name, 0) + 1
            
            segment_stats = [
                {'segment_name': name, 'client_count': count}
                for name, count in segment_counts.items()
            ]
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'total_clients': len(clients_data),
                'n_clusters': get_n_clusters(model),
                'clients': clients_data,
                'segment_stats': segment_stats,
                'model': 'KMeans Client Segmentation (Balkis)',
                'timestamp': datetime.now().isoformat()
            }), 200
            
    except FileNotFoundError:
        return jsonify({'error': 'Modèle non trouvé'}), 404
    except pyodbc.Error as e:
        return jsonify({'error': 'Erreur de connexion au Data Warehouse', 'details': str(e)}), 500
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/balkis/best-seller-b2c', methods=['POST'])
@jwt_required()
def balkis_best_seller_b2c():
    """
    Prédit si un produit est un Best Seller en B2C (Balkis)
    Utilise le Random Forest Classifier avec les données du DWH
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        product_id = data.get('product_id')
        if not product_id:
            return jsonify({'error': 'product_id est requis'}), 400
        
        # Charger le modèle avec joblib
        model_path = 'ml_models/Balkis/rf_classifier_prod.pkl'
        model = joblib.load(model_path)
        
        # Connexion au DWH pour récupérer les features du produit
        conn = get_dwh_connection()
        cursor = conn.cursor()
        
        # Récupérer les stats de vente B2C pour ce produit
        stats_query = """
            SELECT 
                COALESCE(SUM(f.Quantite), 0) AS Total_Qty,
                COALESCE(COUNT(DISTINCT f.Num_facture), 0) AS Nb_Commandes,
                COALESCE(COUNT(DISTINCT f.Id_Entreprise), 0) AS Nb_Clients,
                COALESCE(SUM(f.Prix_Total_HT), 0) AS CA_HT,
                COALESCE(AVG(f.Quantite), 0) AS Avg_Qty,
                COALESCE(AVG(f.Prix_Total_HT), 0) AS Avg_CA,
                COALESCE(p.PU_HT, 0) AS PU_HT
            FROM dbo.Dim_Produit_Sougui p
            LEFT JOIN dbo.Fact_Vente_B2B f ON p.Id_Produit = f.Id_Produit AND f.Type = 'Facture'
            WHERE p.Id_Produit = ?
            GROUP BY p.PU_HT
        """
        cursor.execute(stats_query, (product_id,))
        stats_row = cursor.fetchone()
        
        # Récupérer les ventes des 3 derniers mois
        recent_query = """
            SELECT TOP 3
                SUM(f.Quantite) AS Qty_Mois,
                COUNT(DISTINCT f.Num_facture) AS Cmd_Mois
            FROM dbo.Fact_Vente_B2B f
            INNER JOIN dbo.Dim_Date d ON f.Date_Key = d.Date_Key
            WHERE f.Id_Produit = ? AND f.Type = 'Facture' AND f.Quantite > 0
            GROUP BY d.Annee, d.Mois
            ORDER BY d.Annee DESC, d.Mois DESC
        """
        cursor.execute(recent_query, (product_id,))
        recent_rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Construire les features
        total_qty = float(stats_row[0]) if stats_row[0] else 0.0
        nb_commandes = int(stats_row[1]) if stats_row[1] else 0
        nb_clients = int(stats_row[2]) if stats_row[2] else 0
        ca_ht = float(stats_row[3]) if stats_row[3] else 0.0
        avg_qty = float(stats_row[4]) if stats_row[4] else 0.0
        avg_ca = float(stats_row[5]) if stats_row[5] else 0.0
        pu_ht = float(stats_row[6]) if stats_row[6] else 0.0
        
        lag_1 = float(recent_rows[0][0]) if len(recent_rows) > 0 and recent_rows[0][0] else 0.0
        lag_2 = float(recent_rows[1][0]) if len(recent_rows) > 1 and recent_rows[1][0] else 0.0
        lag_3 = float(recent_rows[2][0]) if len(recent_rows) > 2 and recent_rows[2][0] else 0.0
        rolling_mean_3 = (lag_1 + lag_2 + lag_3) / 3 if (lag_1 + lag_2 + lag_3) > 0 else 0.0
        
        # Features pour le modèle RF - Le modèle attend 4 features
        # Utiliser les features les plus importantes: total_qty, nb_commandes, ca_ht, rolling_mean_3
        features = [total_qty, nb_commandes, ca_ht, rolling_mean_3]
        
        # Faire la prédiction
        prediction = model.predict([features])
        probability = model.predict_proba([features])
        
        # Résultat - gérer Pipeline ou modèle direct
        is_best_seller = int(prediction[0]) == 1
        
        # Récupérer les classes (peut être dans un Pipeline)
        if hasattr(model, 'classes_'):
            classes = model.classes_.tolist()
        elif hasattr(model, 'named_steps'):
            # Pipeline: prendre les classes du dernier estimateur
            final_step = model.steps[-1][1]
            classes = final_step.classes_.tolist() if hasattr(final_step, 'classes_') else [0, 1]
        else:
            classes = [0, 1]
        
        # Trouver l'index de la classe positive
        if 1 in classes:
            pos_index = classes.index(1)
            best_seller_prob = float(probability[0][pos_index]) * 100
        else:
            best_seller_prob = float(max(probability[0])) * 100
        
        return jsonify({
            'product_id': product_id,
            'is_best_seller': is_best_seller,
            'best_seller_probability': round(best_seller_prob, 1),
            'prediction_label': 'Best Seller' if is_best_seller else 'Non Best Seller',
            'features_used': {
                'total_qty': total_qty,
                'nb_commandes': nb_commandes,
                'nb_clients': nb_clients,
                'ca_ht': round(ca_ht, 2),
                'avg_qty': round(avg_qty, 2),
                'pu_ht': pu_ht,
                'lag_1': lag_1,
                'lag_2': lag_2,
                'lag_3': lag_3,
                'rolling_mean_3': round(rolling_mean_3, 2)
            },
            'model': 'Random Forest Classifier (Balkis)',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except FileNotFoundError:
        return jsonify({'error': 'Modèle non trouvé'}), 404
    except pyodbc.Error as e:
        return jsonify({'error': 'Erreur de connexion au Data Warehouse', 'details': str(e)}), 500
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500




# ============================================================================
# MARIEM - Régression et Clustering Géographique
# ============================================================================

@ml_bp.route('/mariem/predict', methods=['POST'])
@jwt_required()
def mariem_predict():
    """
    Prédiction avec régression linéaire (Mariem)
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Charger le modèle et le scaler
        model_path = 'ml_models/Mariem/linear_regression_model.pkl'
        scaler_path = 'ml_models/Mariem/scaler_geo.pkl'
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        
        # Préparer les données
        features = data.get('features', [])
        
        if not features:
            return jsonify({'error': 'Features manquantes'}), 400
        
        # Normaliser et prédire
        features_scaled = scaler.transform([features])
        prediction = model.predict(features_scaled)
        
        return jsonify({
            'prediction': float(prediction[0]),
            'model': 'Linear Regression',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except FileNotFoundError:
        return jsonify({'error': 'Modèle non trouvé'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/mariem/cluster-geo', methods=['POST'])
@jwt_required()
def mariem_cluster_geo():
    """
    Clustering géographique (Mariem)
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Charger le modèle et le scaler
        model_path = 'ml_models/Mariem/kmeans_model.pkl'
        scaler_path = 'ml_models/Mariem/scaler_kmeans.pkl'
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        
        # Préparer les données
        features = data.get('features', [])
        
        if not features:
            return jsonify({'error': 'Features manquantes'}), 400
        
        # Normaliser et prédire le cluster
        features_scaled = scaler.transform([features])
        cluster = model.predict(features_scaled)
        
        return jsonify({
            'cluster': int(cluster[0]),
            'n_clusters': model.n_clusters,
            'model': 'KMeans Geographic Clustering',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except FileNotFoundError:
        return jsonify({'error': 'Modèle non trouvé'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# RAMI - Prédiction de produits
# ============================================================================

@ml_bp.route('/rami/predict', methods=['POST'])
@jwt_required()
def rami_predict():
    """
    Prédiction de produits (Rami)
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Charger le modèle et les encodeurs (saved with joblib)
        model_path = 'ml_models/Rami/best_model.pkl'
        encoder_ref_path = 'ml_models/Rami/encoder_produit_reference.pkl'
        encoder_desc_path = 'ml_models/Rami/encoder_produit_description.pkl'
        features_path = 'ml_models/Rami/feature_list.pkl'
        
        model = joblib.load(model_path)
        encoder_ref = joblib.load(encoder_ref_path)
        encoder_desc = joblib.load(encoder_desc_path)
        feature_list = joblib.load(features_path)
        
        # Préparer les données
        input_data = data.get('data', {})
        
        if not input_data:
            return jsonify({'error': 'Données manquantes'}), 400
        
        # Faire la prédiction
        # Adapter selon la structure attendue par le modèle
        prediction = model.predict([input_data.get('features', [])])
        
        return jsonify({
            'prediction': prediction.tolist() if hasattr(prediction, 'tolist') else prediction,
            'model': 'Product Prediction Model',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except FileNotFoundError as e:
        return jsonify({'error': f'Modèle non trouvé: {str(e)}'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Routes générales
# ============================================================================

@ml_bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    """
    Récupère la liste de tous les produits disponibles pour les prédictions
    """
    try:
        current_user_id = get_jwt_identity()
        from models import db, Produit
        
        # Récupérer tous les produits
        products = Produit.query.all()
        
        products_list = []
        for product in products:
            products_list.append({
                'Id_Produit': product.Id_Produit,
                'Produit_Reference': product.Produit_Reference,
                'Produit_Nom': product.Produit_Nom,
                'Produit_Description': product.Produit_Description,
                'Produit_Categorie': product.Produit_Categorie,
                'Produit_PU_HT': float(product.Produit_PU_HT) if product.Produit_PU_HT else 0.0
            })
        
        return jsonify({
            'products': products_list,
            'count': len(products_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/dwh/products', methods=['GET'])
@jwt_required()
def get_dwh_products():
    """
    Récupère les produits depuis le Data Warehouse SQL Server
    Supporte la recherche par nom et référence
    
    Query Parameters:
    - search: Recherche par nom ou référence (optionnel)
    - limit: Nombre maximum de résultats (défaut: 100)
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Récupérer les paramètres de recherche
        search_term = request.args.get('search', '').strip()
        limit = request.args.get('limit', 100, type=int)
        
        # Connexion au DWH
        conn = get_dwh_connection()
        cursor = conn.cursor()
        
        # Construire la requête SQL
        # Utiliser COALESCE pour gérer les valeurs NULL et utiliser Description si Nom est NULL
        if search_term:
            query = """
                SELECT DISTINCT TOP (?)
                    p.Id_Produit,
                    p.Reference AS Produit_Reference,
                    p.Description AS Produit_Description,
                    COALESCE(p.Nom, p.Description) AS Produit_Nom,
                    COALESCE(p.Categorie, 'Non catégorisé') AS Produit_Categorie,
                    COALESCE(p.PU_HT, 0.0) AS Produit_PU_HT,
                    COALESCE(p.Source, 'N/A') AS Produit_Source,
                    COALESCE(p.En_Stock, 0) AS Produit_En_Stock,
                    COUNT(DISTINCT f.Num_facture) AS Nb_Ventes
                FROM dbo.Dim_Produit_Sougui p
                LEFT JOIN dbo.Fact_Vente_B2B f ON p.Id_Produit = f.Id_Produit
                WHERE 
                    (p.Nom LIKE ? OR 
                     p.Reference LIKE ? OR 
                     p.Description LIKE ?)
                GROUP BY 
                    p.Id_Produit, p.Reference, p.Description, p.Nom, 
                    p.Categorie, p.PU_HT, p.Source, p.En_Stock
                ORDER BY Nb_Ventes DESC, COALESCE(p.Nom, p.Description) ASC
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (limit, search_pattern, search_pattern, search_pattern))
        else:
            query = """
                SELECT DISTINCT TOP (?)
                    p.Id_Produit,
                    p.Reference AS Produit_Reference,
                    p.Description AS Produit_Description,
                    COALESCE(p.Nom, p.Description) AS Produit_Nom,
                    COALESCE(p.Categorie, 'Non catégorisé') AS Produit_Categorie,
                    COALESCE(p.PU_HT, 0.0) AS Produit_PU_HT,
                    COALESCE(p.Source, 'N/A') AS Produit_Source,
                    COALESCE(p.En_Stock, 0) AS Produit_En_Stock,
                    COUNT(DISTINCT f.Num_facture) AS Nb_Ventes
                FROM dbo.Dim_Produit_Sougui p
                LEFT JOIN dbo.Fact_Vente_B2B f ON p.Id_Produit = f.Id_Produit
                GROUP BY 
                    p.Id_Produit, p.Reference, p.Description, p.Nom, 
                    p.Categorie, p.PU_HT, p.Source, p.En_Stock
                ORDER BY Nb_Ventes DESC, COALESCE(p.Nom, p.Description) ASC
            """
            cursor.execute(query, (limit,))
        
        # Récupérer les résultats
        columns = [column[0] for column in cursor.description]
        results = cursor.fetchall()
        
        # Convertir en liste de dictionnaires
        products_list = []
        for row in results:
            product_dict = {}
            for i, column in enumerate(columns):
                value = row[i]
                # Convertir les types spéciaux
                if isinstance(value, (int, float)):
                    product_dict[column] = float(value) if isinstance(value, float) else int(value)
                elif value is None:
                    product_dict[column] = None
                else:
                    product_dict[column] = str(value).strip()
            
            products_list.append(product_dict)
        
        # Fermer la connexion
        cursor.close()
        conn.close()
        
        return jsonify({
            'products': products_list,
            'count': len(products_list),
            'search_term': search_term if search_term else None,
            'source': 'SQL Server DWH'
        }), 200
        
    except pyodbc.Error as e:
        return jsonify({
            'error': 'Erreur de connexion au Data Warehouse',
            'details': str(e)
        }), 500
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/dwh/products/<int:product_id>', methods=['GET'])
@jwt_required()
def get_dwh_product_details(product_id):
    """
    Récupère les détails d'un produit spécifique depuis le DWH
    avec son historique de ventes
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Connexion au DWH
        conn = get_dwh_connection()
        cursor = conn.cursor()
        
        # Récupérer les informations du produit
        product_query = """
            SELECT 
                p.Id_Produit,
                p.Reference AS Produit_Reference,
                p.Description AS Produit_Description,
                COALESCE(p.Nom, p.Description) AS Produit_Nom,
                COALESCE(p.Categorie, 'Non catégorisé') AS Produit_Categorie,
                COALESCE(p.PU_HT, 0.0) AS Produit_PU_HT,
                COALESCE(p.Source, 'N/A') AS Produit_Source,
                COALESCE(p.Tarif_Regulier, 0.0) AS Tarif_Regulier,
                COALESCE(p.Tarif_Promo, 0.0) AS Tarif_Promo,
                COALESCE(p.En_Stock, 0) AS Produit_En_Stock
            FROM dbo.Dim_Produit_Sougui p
            WHERE p.Id_Produit = ?
        """
        cursor.execute(product_query, (product_id,))
        product_row = cursor.fetchone()
        
        if not product_row:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Produit non trouvé'}), 404
        
        # Convertir en dictionnaire
        product_columns = [column[0] for column in cursor.description]
        product_info = {}
        for i, column in enumerate(product_columns):
            value = product_row[i]
            if isinstance(value, (int, float)):
                product_info[column] = float(value) if isinstance(value, float) else int(value)
            elif value is None:
                product_info[column] = None
            else:
                product_info[column] = str(value).strip()
        
        # Récupérer l'historique des ventes (12 derniers mois)
        history_query = """
            SELECT TOP 12
                d.Annee,
                d.Mois,
                d.Nom_Mois,
                d.Trimestre,
                SUM(f.Quantite) AS Quantite_Totale,
                COUNT(DISTINCT f.Num_facture) AS Nb_Commandes,
                COUNT(DISTINCT f.Id_Entreprise) AS Nb_Clients,
                SUM(f.Prix_Total_HT) AS CA_HT,
                AVG(f.Prix_Total_HT) AS Prix_Moyen
            FROM dbo.Fact_Vente_B2B f
            INNER JOIN dbo.Dim_Date d ON f.Date_Key = d.Date_Key
            WHERE f.Id_Produit = ?
                AND f.Type = 'Facture'
                AND f.Quantite > 0
            GROUP BY d.Annee, d.Mois, d.Nom_Mois, d.Trimestre
            ORDER BY d.Annee DESC, d.Mois DESC
        """
        cursor.execute(history_query, (product_id,))
        history_rows = cursor.fetchall()
        
        # Convertir l'historique en liste
        history_list = []
        for row in history_rows:
            history_list.append({
                'Annee': int(row[0]),
                'Mois': int(row[1]),
                'Nom_Mois': str(row[2]).strip(),
                'Trimestre': int(row[3]),
                'Quantite_Totale': float(row[4]) if row[4] else 0.0,
                'Nb_Commandes': int(row[5]) if row[5] else 0,
                'Nb_Clients': int(row[6]) if row[6] else 0,
                'CA_HT': float(row[7]) if row[7] else 0.0,
                'Prix_Moyen': float(row[8]) if row[8] else 0.0
            })
        
        # Statistiques globales
        stats_query = """
            SELECT 
                COUNT(DISTINCT f.Num_facture) AS Total_Factures,
                COUNT(DISTINCT f.Id_Entreprise) AS Total_Clients,
                SUM(f.Quantite) AS Total_Quantite,
                SUM(f.Prix_Total_HT) AS Total_CA_HT,
                MIN(d.Full_Date) AS Premiere_Vente,
                MAX(d.Full_Date) AS Derniere_Vente
            FROM dbo.Fact_Vente_B2B f
            INNER JOIN dbo.Dim_Date d ON f.Date_Key = d.Date_Key
            WHERE f.Id_Produit = ?
                AND f.Type = 'Facture'
                AND f.Quantite > 0
        """
        cursor.execute(stats_query, (product_id,))
        stats_row = cursor.fetchone()
        
        stats = {}
        if stats_row:
            stats = {
                'Total_Factures': int(stats_row[0]) if stats_row[0] else 0,
                'Total_Clients': int(stats_row[1]) if stats_row[1] else 0,
                'Total_Quantite': float(stats_row[2]) if stats_row[2] else 0.0,
                'Total_CA_HT': float(stats_row[3]) if stats_row[3] else 0.0,
                'Premiere_Vente': str(stats_row[4]) if stats_row[4] else None,
                'Derniere_Vente': str(stats_row[5]) if stats_row[5] else None
            }
        
        # Fermer la connexion
        cursor.close()
        conn.close()
        
        return jsonify({
            'product': product_info,
            'sales_history': history_list,
            'statistics': stats,
            'source': 'SQL Server DWH'
        }), 200
        
    except pyodbc.Error as e:
        return jsonify({
            'error': 'Erreur de connexion au Data Warehouse',
            'details': str(e)
        }), 500
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/predict', methods=['POST'])
@jwt_required()
def predict_demand():
    """
    Prédiction de la demande pour un produit spécifique
    """
    try:
        current_user_id = get_jwt_identity()
        from models import db, Produit, Commande, LigneCommande
        from sqlalchemy import func, extract
        from datetime import datetime
        import calendar
        
        data = request.get_json()
        product_id = data.get('product_id')
        
        if not product_id:
            return jsonify({'error': 'product_id manquant'}), 400
        
        # Récupérer le produit
        product = Produit.query.get(product_id)
        if not product:
            return jsonify({'error': 'Produit non trouvé'}), 404
        
        # Récupérer l'historique des ventes (6 derniers mois)
        historical_data = db.session.query(
            extract('year', Commande.Date_Commande).label('Annee'),
            extract('month', Commande.Date_Commande).label('Mois'),
            func.sum(LigneCommande.Quantite).label('Quantite_Totale'),
            func.count(func.distinct(Commande.Id_Commande)).label('Nb_Commandes'),
            func.count(func.distinct(Commande.Id_Client)).label('Nb_Clients')
        ).join(
            LigneCommande, Commande.Id_Commande == LigneCommande.Id_Commande
        ).filter(
            LigneCommande.Id_Produit == product_id
        ).group_by(
            extract('year', Commande.Date_Commande),
            extract('month', Commande.Date_Commande)
        ).order_by(
            extract('year', Commande.Date_Commande).desc(),
            extract('month', Commande.Date_Commande).desc()
        ).limit(6).all()
        
        if len(historical_data) < 3:
            return jsonify({
                'error': 'Données insuffisantes pour ce produit',
                'available_months': len(historical_data),
                'required_months': 3
            }), 400
        
        # Convertir en liste de dictionnaires
        hist_list = []
        quantities = []
        for h in historical_data:
            hist_list.append({
                'Annee': int(h.Annee),
                'Mois': int(h.Mois),
                'Quantite_Totale': int(h.Quantite_Totale),
                'Nb_Commandes': int(h.Nb_Commandes),
                'Nb_Clients': int(h.Nb_Clients)
            })
            quantities.append(int(h.Quantite_Totale))
        
        # Inverser pour avoir l'ordre chronologique
        hist_list.reverse()
        quantities.reverse()
        
        # Calculer les statistiques
        avg_quantity = sum(quantities) / len(quantities)
        min_quantity = min(quantities)
        max_quantity = max(quantities)
        
        # Calculer la tendance
        if len(quantities) >= 2:
            recent_avg = sum(quantities[-3:]) / min(3, len(quantities))
            old_avg = sum(quantities[:3]) / min(3, len(quantities))
            trend_percentage = ((recent_avg - old_avg) / old_avg * 100) if old_avg > 0 else 0
            
            if trend_percentage > 10:
                trend_direction = 'croissante'
            elif trend_percentage < -10:
                trend_direction = 'décroissante'
            else:
                trend_direction = 'stable'
        else:
            trend_percentage = 0
            trend_direction = 'stable'
        
        # Calculer la volatilité (coefficient de variation)
        if avg_quantity > 0:
            std_dev = (sum((q - avg_quantity) ** 2 for q in quantities) / len(quantities)) ** 0.5
            volatility = (std_dev / avg_quantity) * 100
        else:
            volatility = 0
        
        # Détection de saisonnalité simple
        seasonality_detected = max(quantities) > avg_quantity * 1.5 if avg_quantity > 0 else False
        
        # Qualité des données
        if len(historical_data) >= 6:
            data_quality = 'excellent'
        elif len(historical_data) >= 4:
            data_quality = 'good'
        else:
            data_quality = 'acceptable'
        
        # Générer les prédictions pour les 3 prochains mois
        predictions = []
        current_date = datetime.now()
        
        for i in range(1, 4):
            month = (current_date.month + i - 1) % 12 + 1
            year = current_date.year + (current_date.month + i - 1) // 12
            
            # Prédiction simple basée sur la moyenne et la tendance
            base_prediction = avg_quantity * (1 + trend_percentage / 100) ** i
            
            # Ajouter un facteur saisonnier aléatoire
            seasonal_factor = 1.0
            if seasonality_detected:
                # Simuler une variation saisonnière
                seasonal_factor = 0.9 + (month % 3) * 0.1
            
            predicted_quantity = base_prediction * seasonal_factor
            
            # Calculer les bornes de confiance
            confidence = max(60, min(95, 85 - volatility / 2))
            margin = predicted_quantity * (1 - confidence / 100)
            
            predictions.append({
                'month': month,
                'year': year,
                'month_name': calendar.month_name[month],
                'predicted_quantity': round(predicted_quantity, 2),
                'lower_bound': round(max(0, predicted_quantity - margin), 2),
                'upper_bound': round(predicted_quantity + margin, 2),
                'confidence': round(confidence, 1),
                'trimestre': ((month - 1) // 3) + 1,
                'seasonal_factor': round(seasonal_factor, 2)
            })
        
        # Calculer la confiance moyenne
        avg_confidence = sum(p['confidence'] for p in predictions) / len(predictions)
        
        response = {
            'product': {
                'id': product.Id_Produit,
                'name': product.Produit_Nom,
                'reference': product.Produit_Reference,
                'description': product.Produit_Description,
                'price': float(product.Produit_PU_HT) if product.Produit_PU_HT else 0.0,
                'category': product.Produit_Categorie
            },
            'predictions': predictions,
            'analysis': {
                'trend_direction': trend_direction,
                'trend_percentage': round(trend_percentage, 1),
                'volatility': round(volatility, 1),
                'average_confidence': round(avg_confidence, 1),
                'seasonality_detected': seasonality_detected,
                'data_quality': data_quality
            },
            'historical_data': {
                'last_6_months': hist_list,
                'avg_quantity': round(avg_quantity, 2),
                'min_quantity': min_quantity,
                'max_quantity': max_quantity,
                'avg_orders': round(sum(h['Nb_Commandes'] for h in hist_list) / len(hist_list), 1),
                'avg_clients': round(sum(h['Nb_Clients'] for h in hist_list) / len(hist_list), 1),
                'total_months': len(historical_data)
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/model-info', methods=['GET'])
@jwt_required()
def get_model_info():
    """
    Informations sur le modèle ML utilisé
    """
    current_user_id = get_jwt_identity()
    return jsonify({
        'model_type': 'Time Series Forecasting',
        'features_count': 5,
        'features': [
            'Historical Sales Data',
            'Trend Analysis',
            'Seasonality Detection',
            'Volatility Calculation',
            'Confidence Intervals'
        ],
        'status': 'active',
        'description': 'Modèle de prédiction de la demande basé sur l\'analyse des séries temporelles'
    }), 200


@ml_bp.route('/models', methods=['GET'])
@jwt_required()
def list_models():
    """
    Liste tous les modèles ML disponibles
    """
    current_user_id = get_jwt_identity()
    models = {
        'balkis': {
            'classifier': {
                'name': 'Random Forest Classifier',
                'endpoint': '/api/ml/balkis/classify',
                'description': 'Classification avec Random Forest'
            },
            'clustering': {
                'name': 'KMeans Clustering',
                'endpoint': '/api/ml/balkis/cluster',
                'description': 'Clustering avec KMeans'
            },
            'best_seller_b2c': {
                'name': 'Best Seller B2C',
                'endpoint': '/api/ml/balkis/best-seller-b2c',
                'description': 'Prédiction Best Seller en B2C'
            },
            'client_segmentation': {
                'name': 'Client Segmentation',
                'endpoint': '/api/ml/balkis/client-segmentation',
                'description': 'Segmentation des clients par comportement'
            }
        },
        'mariem': {
            'regression': {
                'name': 'Linear Regression',
                'endpoint': '/api/ml/mariem/predict',
                'description': 'Prédiction avec régression linéaire'
            },
            'geo_clustering': {
                'name': 'Geographic KMeans',
                'endpoint': '/api/ml/mariem/cluster-geo',
                'description': 'Clustering géographique'
            }
        },
        'rami': {
            'product_prediction': {
                'name': 'Product Prediction',
                'endpoint': '/api/ml/rami/predict',
                'description': 'Prédiction de produits'
            }
        }
    }
    
    return jsonify(models), 200


@ml_bp.route('/rami/predict-demand', methods=['POST'])
@jwt_required()
def rami_predict_demand():
    """
    Prédiction de la demande pour un produit B2B sur les 3 prochains mois (Rami)
    Utilise le Data Warehouse SQL Server (pyodbc) pour les données historiques
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Charger le modèle et les encodeurs
        model_path = 'ml_models/Rami/best_model.pkl'
        encoder_ref_path = 'ml_models/Rami/encoder_produit_reference.pkl'
        encoder_desc_path = 'ml_models/Rami/encoder_produit_description.pkl'
        features_path = 'ml_models/Rami/feature_list.pkl'
        
        model = joblib.load(model_path)
        encoder_ref = joblib.load(encoder_ref_path)
        encoder_desc = joblib.load(encoder_desc_path)
        feature_list = joblib.load(features_path)
        
        # Récupérer les données du produit
        product_id = data.get('product_id')
        product_reference = data.get('product_reference', '')
        product_description = data.get('product_description', '')
        product_pu_ht = float(data.get('product_pu_ht', 0.0))
        
        if not product_id:
            return jsonify({'error': 'product_id est requis'}), 400
        
        # ── Connexion au DWH pour les données historiques ──
        conn = get_dwh_connection()
        cursor = conn.cursor()
        
        # Récupérer les 6 derniers mois de ventes pour ce produit
        hist_query = """
            SELECT TOP 6
                d.Annee,
                d.Mois,
                SUM(f.Quantite) AS Quantite_Totale,
                COUNT(DISTINCT f.Num_facture) AS Nb_Commandes,
                COUNT(DISTINCT f.Id_Entreprise) AS Nb_Clients,
                SUM(f.Prix_Total_HT) AS CA_HT
            FROM dbo.Fact_Vente_B2B f
            INNER JOIN dbo.Dim_Date d ON f.Date_Key = d.Date_Key
            WHERE f.Id_Produit = ?
                AND f.Type = 'Facture'
                AND f.Quantite > 0
            GROUP BY d.Annee, d.Mois
            ORDER BY d.Annee DESC, d.Mois DESC
        """
        cursor.execute(hist_query, (product_id,))
        historical_rows = cursor.fetchall()
        
        # Fermer la connexion DWH
        cursor.close()
        conn.close()
        
        # Calculer les lags et les statistiques historiques
        if len(historical_rows) < 3:
            lag_1 = 100.0
            lag_2 = 100.0
            lag_3 = 100.0
            rolling_mean_3 = 100.0
            nb_commandes = 2
            nb_clients = 1
            ca_ht = product_pu_ht * 100
            avg_qty_per_order = 50.0
            avg_clients_per_order = 1.0
        else:
            # Lags: most recent month = lag_1, etc.
            lag_1 = float(historical_rows[0][2]) if historical_rows[0][2] else 100.0
            lag_2 = float(historical_rows[1][2]) if len(historical_rows) > 1 and historical_rows[1][2] else 100.0
            lag_3 = float(historical_rows[2][2]) if len(historical_rows) > 2 and historical_rows[2][2] else 100.0
            rolling_mean_3 = (lag_1 + lag_2 + lag_3) / 3
            nb_commandes = int(historical_rows[0][3]) if historical_rows[0][3] else 2
            nb_clients = int(historical_rows[0][4]) if historical_rows[0][4] else 1
            ca_ht = float(historical_rows[0][5]) if historical_rows[0][5] else product_pu_ht * 100
            
            # Calculer les ratios pour estimer les mois futurs
            avg_qty_per_order = lag_1 / max(nb_commandes, 1)
            avg_clients_per_order = nb_clients / max(nb_commandes, 1)
        
        # Calculer la tendance sur les données historiques disponibles
        if len(historical_rows) >= 3:
            quantities = [float(r[2]) if r[2] else 0.0 for r in historical_rows[:min(6, len(historical_rows))]]
            quantities.reverse()  # Chronological order
            recent_avg = sum(quantities[-3:]) / 3
            older_avg = sum(quantities[:3]) / len(quantities[:3])
            trend_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        else:
            trend_pct = 0
        
        # Prédire pour les 3 prochains mois
        now = datetime.now()
        predictions = []
        
        for i in range(1, 4):
            # Calculer le mois et l'année
            target_month = now.month + i
            target_year = now.year
            
            if target_month > 12:
                target_month -= 12
                target_year += 1
            
            trimestre = (target_month - 1) // 3 + 1
            is_q4 = 1 if trimestre == 4 else 0
            
            # Encoder les références
            try:
                ref_encoded = encoder_ref.transform([product_reference])[0]
            except:
                ref_encoded = 0
            
            try:
                desc_encoded = encoder_desc.transform([product_description])[0]
            except:
                desc_encoded = 0
            
            # Estimer nb_commandes, nb_clients, ca_ht pour ce mois
            # Basé sur la prédiction précédente et les ratios historiques
            if i > 1 and predictions:
                prev_qty = predictions[-1]['quantity']
                est_nb_commandes = max(1, round(prev_qty / max(avg_qty_per_order, 1)))
                est_nb_clients = max(1, round(est_nb_commandes * avg_clients_per_order))
                est_ca_ht = prev_qty * product_pu_ht
            else:
                est_nb_commandes = nb_commandes
                est_nb_clients = nb_clients
                est_ca_ht = ca_ht
            
            # Créer les features
            features_dict = {
                'Mois': target_month,
                'Annee': target_year,
                'Trimestre': trimestre,
                'Is_Q4': is_q4,
                'Mois_Sin': np.sin(2 * np.pi * target_month / 12),
                'Mois_Cos': np.cos(2 * np.pi * target_month / 12),
                'Ref_Encoded': ref_encoded,
                'Desc_Encoded': desc_encoded,
                'Produit_PU_HT': product_pu_ht,
                'Nb_Commandes': est_nb_commandes,
                'Nb_Clients': est_nb_clients,
                'CA_HT': est_ca_ht,
                'Lag_1': lag_1,
                'Lag_2': lag_2,
                'Lag_3': lag_3,
                'Rolling_Mean_3': rolling_mean_3
            }
            
            # Créer le DataFrame avec les features dans le bon ordre
            input_df = pd.DataFrame([features_dict])[feature_list]
            
            # Faire la prédiction
            prediction = model.predict(input_df)[0]
            prediction = max(0.0, float(prediction))  # Pas de quantités négatives
            
            # Appliquer un ajustement saisonnier léger basé sur la tendance
            seasonal_adj = 1.0 + (trend_pct / 100) * (i * 0.3)
            # Ajustement Q4: les ventes B2B augmentent en fin d'année
            if is_q4:
                seasonal_adj *= 1.05
            prediction = prediction * seasonal_adj
            prediction = max(0.0, round(prediction, 1))
            
            # Nom du mois en français
            month_names_fr = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
            month_name = f"{month_names_fr[target_month-1]} {target_year}"
            
            predictions.append({
                'month': month_name,
                'quantity': round(prediction, 0)
            })
            
            # Mettre à jour les lags et rolling mean pour le mois suivant
            lag_3 = lag_2
            lag_2 = lag_1
            lag_1 = prediction
            rolling_mean_3 = (lag_1 + lag_2 + lag_3) / 3
        
        return jsonify({
            'predictions': predictions,
            'product_id': product_id,
            'product_reference': product_reference,
            'model': 'Gradient Boosting Regressor',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except pyodbc.Error as e:
        return jsonify({
            'error': 'Erreur de connexion au Data Warehouse',
            'details': str(e)
        }), 500
    except FileNotFoundError as e:
        return jsonify({'error': f'Modèle non trouvé: {str(e)}'}), 404
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ELYES - Price Simulator
# ============================================================================

@ml_bp.route('/elyes/price-simulator', methods=['POST'])
@jwt_required()
def elyes_price_simulator():
    """
    Simulateur de prix avec analyse de compétitivité (Elyes)
    Utilise Random Forest pour analyser la position concurrentielle
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        product_reference = data.get('product_reference')
        new_price = data.get('new_price')
        
        if not product_reference or new_price is None:
            return jsonify({'error': 'product_reference et new_price sont requis'}), 400
        
        # Charger le modèle et le scaler
        model_path = 'ml_models/Elyes/rf_model.pkl'
        scaler_path = 'ml_models/Elyes/scaler.pkl'
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        # Connexion au DWH pour récupérer les données produit et concurrents
        conn = get_dwh_connection()
        cursor = conn.cursor()
        
        # Récupérer les informations du produit Sougui
        sougui_query = """
            SELECT 
                Id_Produit,
                Reference,
                Nom,
                PU_HT,
                En_Stock
            FROM dbo.Dim_Produit_Sougui
            WHERE Reference = ?
        """
        cursor.execute(sougui_query, (product_reference,))
        sougui_product = cursor.fetchone()
        
        if not sougui_product:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Produit non trouvé dans Sougui'}), 404
        
        current_price = float(sougui_product[3]) if sougui_product[3] else 0.0
        product_name = sougui_product[2]
        
        # Récupérer les prix des concurrents (Kalys et Ileycom)
        kalys_query = """
            SELECT AVG(CAST(Price AS FLOAT)) as Avg_Price
            FROM dbo.Dim_Produit_Kalys
            WHERE Reference = ?
        """
        cursor.execute(kalys_query, (product_reference,))
        kalys_result = cursor.fetchone()
        kalys_price = float(kalys_result[0]) if kalys_result and kalys_result[0] else None
        
        ileycom_query = """
            SELECT AVG(CAST(Price AS FLOAT)) as Avg_Price
            FROM dbo.Dim_Produit_Ileyckom
            WHERE Reference = ?
        """
        cursor.execute(ileycom_query, (product_reference,))
        ileycom_result = cursor.fetchone()
        ileycom_price = float(ileycom_result[0]) if ileycom_result and ileycom_result[0] else None
        
        # Si pas de concurrents, utiliser des moyennes par défaut
        if kalys_price is None:
            kalys_price = current_price * 0.95  # Estimation
        if ileycom_price is None:
            ileycom_price = current_price * 1.05  # Estimation
        
        # Calculer le prix concurrent moyen
        avg_competitor_price = (kalys_price + ileycom_price) / 2
        
        # Préparer les features pour le modèle ML
        # Features: [PU_HT, Kalys_Price, Ileycom_Price, Has_Kalys, Has_Ileycom]
        features_current = [
            current_price,
            kalys_price,
            ileycom_price,
            1 if kalys_price else 0,
            1 if ileycom_price else 0
        ]
        
        features_new = [
            new_price,
            kalys_price,
            ileycom_price,
            1 if kalys_price else 0,
            1 if ileycom_price else 0
        ]
        
        # Normaliser les features
        features_current_scaled = scaler.transform([features_current])
        features_new_scaled = scaler.transform([features_new])
        
        # Prédictions ML
        current_prediction = model.predict(features_current_scaled)[0]
        new_prediction = model.predict(features_new_scaled)[0]
        
        current_proba = model.predict_proba(features_current_scaled)[0]
        new_proba = model.predict_proba(features_new_scaled)[0]
        
        # Analyse de compétitivité améliorée
        price_difference = new_price - avg_competitor_price
        price_change = new_price - current_price
        price_change_pct = (price_change / current_price) * 100 if current_price > 0 else 0
        
        # Position concurrentielle avec plus de nuances
        if new_price < avg_competitor_price * 0.8:
            position = "Much_Cheaper"
            competitiveness = "Highly_Competitive"
            competitiveness_score = 95
        elif new_price < avg_competitor_price * 0.9:
            position = "Cheaper"
            competitiveness = "Very_Competitive"
            competitiveness_score = 85
        elif new_price < avg_competitor_price:
            position = "Slightly_Cheaper"
            competitiveness = "Competitive"
            competitiveness_score = 75
        elif new_price < avg_competitor_price * 1.05:
            position = "Similar_Price"
            competitiveness = "Moderately_Competitive"
            competitiveness_score = 65
        elif new_price < avg_competitor_price * 1.15:
            position = "Slightly_More_Expensive"
            competitiveness = "Less_Competitive"
            competitiveness_score = 45
        elif new_price < avg_competitor_price * 1.3:
            position = "More_Expensive"
            competitiveness = "Not_Competitive"
            competitiveness_score = 25
        else:
            position = "Much_More_Expensive"
            competitiveness = "Highly_Uncompetitive"
            competitiveness_score = 10
        
        # Calcul du score de compétitivité global (simulation plus réaliste)
        total_products_query = """
            SELECT COUNT(DISTINCT Reference) 
            FROM dbo.Dim_Produit_Sougui 
            WHERE PU_HT > 0
        """
        cursor.execute(total_products_query)
        total_products = cursor.fetchone()[0] or 1
        
        # Impact sur le score global basé sur la position
        current_competitive = 1 if current_price < avg_competitor_price else 0
        new_competitive = 1 if new_price < avg_competitor_price else 0
        score_impact = (new_competitive - current_competitive) / total_products * 100
        
        # Analyse de l'élasticité des prix (simulation)
        price_elasticity = -1.2  # Élasticité typique pour les produits artisanaux
        demand_change_pct = price_elasticity * price_change_pct
        
        # Impact sur le chiffre d'affaires avec élasticité
        base_volume = 100  # Volume de base
        new_volume = base_volume * (1 + demand_change_pct / 100)
        new_volume = max(new_volume, 0)  # Pas de volume négatif
        
        revenue_current = current_price * base_volume
        revenue_new = new_price * new_volume
        revenue_impact = revenue_new - revenue_current
        
        # Analyse des marges (simulation)
        estimated_cost = current_price * 0.6  # Coût estimé à 60% du prix
        margin_current = current_price - estimated_cost
        margin_new = new_price - estimated_cost
        margin_change = margin_new - margin_current
        margin_change_pct = (margin_change / margin_current) * 100 if margin_current > 0 else 0
        
        # Recommandation IA améliorée avec plus de logique business
        if new_price < avg_competitor_price * 0.7:
            recommendation = f"⚠️ Prix très bas ({new_price:.0f} TND). Risque de guerre des prix. Vérifiez la rentabilité (marge estimée: {margin_new:.1f} TND)."
            recommendation_type = "warning"
        elif new_price < avg_competitor_price * 0.85:
            recommendation = f"💚 Excellent positionnement! À {new_price:.0f} TND, vous êtes {((avg_competitor_price-new_price)/avg_competitor_price*100):.1f}% moins cher. Augmentation de volume estimée: {demand_change_pct:.1f}%."
            recommendation_type = "excellent"
        elif new_price < avg_competitor_price:
            recommendation = f"✅ Bon positionnement concurrentiel à {new_price:.0f} TND. Impact volume: {demand_change_pct:.1f}%."
            recommendation_type = "good"
        elif new_price < avg_competitor_price * 1.05:
            recommendation = f"🔶 Prix similaire aux concurrents ({new_price:.0f} TND). Différenciation par la qualité recommandée."
            recommendation_type = "neutral"
        elif new_price < avg_competitor_price * 1.15:
            recommendation = f"⚠️ Prix {(new_price-avg_competitor_price):.0f} TND au-dessus du marché. Baisse de volume estimée: {abs(demand_change_pct):.1f}%."
            recommendation_type = "warning"
        else:
            recommendation = f"🔴 Prix significativement élevé! Risque de perte de parts de marché. Réduction recommandée: {(new_price-avg_competitor_price*1.1):.0f} TND."
            recommendation_type = "danger"
        
        # Classification du segment de prix avec plus de précision
        if new_price < avg_competitor_price * 0.8:
            price_segment = "Budget"
            segment_strategy = "Volume et accessibilité"
        elif new_price < avg_competitor_price * 1.2:
            price_segment = "Mid-range"
            segment_strategy = "Équilibre prix-qualité"
        else:
            price_segment = "Premium"
            segment_strategy = "Différenciation qualité"
        
        # Analyse des risques
        risks = []
        opportunities = []
        
        if price_change_pct < -20:
            risks.append("Guerre des prix potentielle")
            risks.append("Impact sur la perception qualité")
        elif price_change_pct > 20:
            risks.append("Perte de clients sensibles au prix")
            risks.append("Avantage concurrentiel pour les rivaux")
        
        if new_price < avg_competitor_price:
            opportunities.append("Gain de parts de marché")
            opportunities.append("Attraction de nouveaux clients")
        
        if margin_new > margin_current:
            opportunities.append("Amélioration de la rentabilité")
        
        # Prédictions ML améliorées avec contexte
        features_current_scaled = scaler.transform([features_current])
        features_new_scaled = scaler.transform([features_new])
        
        current_prediction = model.predict(features_current_scaled)[0]
        new_prediction = model.predict(features_new_scaled)[0]
        
        current_proba = model.predict_proba(features_current_scaled)[0]
        new_proba = model.predict_proba(features_new_scaled)[0]
        
        # Interprétation des prédictions ML
        ml_interpretation = ""
        if new_prediction != current_prediction:
            if new_prediction == 1:
                ml_interpretation = "Le modèle prédit une amélioration de la compétitivité"
            else:
                ml_interpretation = "Le modèle prédit une dégradation de la compétitivité"
        else:
            ml_interpretation = "Le modèle prédit un maintien de la position concurrentielle"
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'product_reference': product_reference,
            'product_name': product_name,
            'current_price': round(current_price, 2),
            'new_price': round(new_price, 2),
            'price_change': round(price_change, 2),
            'price_change_percentage': round(price_change_pct, 1),
            'competitor_prices': {
                'kalys_price': round(kalys_price, 2) if kalys_price else None,
                'ileycom_price': round(ileycom_price, 2) if ileycom_price else None,
                'average_competitor_price': round(avg_competitor_price, 2)
            },
            'competitiveness_analysis': {
                'price_difference_vs_competitors': round(price_difference, 2),
                'position': position,
                'competitiveness': competitiveness,
                'competitiveness_score': competitiveness_score,
                'price_segment': price_segment,
                'segment_strategy': segment_strategy
            },
            'ml_predictions': {
                'current_prediction': int(current_prediction),
                'new_prediction': int(new_prediction),
                'current_probability': [round(p, 3) for p in current_proba],
                'new_probability': [round(p, 3) for p in new_proba],
                'interpretation': ml_interpretation
            },
            'business_impact': {
                'revenue_impact_per_100_units': round(revenue_impact, 2),
                'competitiveness_score_impact': round(score_impact, 2),
                'demand_change_percentage': round(demand_change_pct, 1),
                'estimated_new_volume': round(new_volume, 1),
                'margin_analysis': {
                    'current_margin': round(margin_current, 2),
                    'new_margin': round(margin_new, 2),
                    'margin_change': round(margin_change, 2),
                    'margin_change_percentage': round(margin_change_pct, 1)
                }
            },
            'recommendation': {
                'message': recommendation,
                'type': recommendation_type
            },
            'risk_analysis': {
                'risks': risks,
                'opportunities': opportunities
            },
            'model': 'Random Forest Price Simulator (Elyes) - Enhanced',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except FileNotFoundError:
        return jsonify({'error': 'Modèle non trouvé'}), 404
    except pyodbc.Error as e:
        return jsonify({
            'error': 'Erreur de connexion au Data Warehouse',
            'details': str(e)
        }), 500
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/elyes/products', methods=['GET'])
@jwt_required()
def elyes_get_products():
    """
    Récupère la liste des produits Sougui avec leurs prix et concurrents
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Connexion au DWH
        conn = get_dwh_connection()
        cursor = conn.cursor()
        
        # Récupérer les produits Sougui avec leurs concurrents
        products_query = """
            WITH SouguiProducts AS (
                SELECT 
                    Id_Produit,
                    Reference,
                    Nom,
                    PU_HT,
                    En_Stock
                FROM dbo.Dim_Produit_Sougui
                WHERE PU_HT > 0
            ),
            KalysPrices AS (
                SELECT 
                    Reference,
                    AVG(CAST(Price AS FLOAT)) as Avg_Price
                FROM dbo.Dim_Produit_Kalys
                GROUP BY Reference
            ),
            IleycomPrices AS (
                SELECT 
                    Reference,
                    AVG(CAST(Price AS FLOAT)) as Avg_Price
                FROM dbo.Dim_Produit_Ileyckom
                GROUP BY Reference
            )
            SELECT 
                s.Id_Produit,
                s.Reference,
                s.Nom,
                s.PU_HT,
                s.En_Stock,
                k.Avg_Price as Kalys_Price,
                i.Avg_Price as Ileycom_Price
            FROM SouguiProducts s
            LEFT JOIN KalysPrices k ON s.Reference = k.Reference
            LEFT JOIN IleycomPrices i ON s.Reference = i.Reference
            WHERE (k.Avg_Price IS NOT NULL OR i.Avg_Price IS NOT NULL)
            ORDER BY s.Reference
        """
        
        cursor.execute(products_query)
        products = cursor.fetchall()
        
        products_list = []
        for product in products:
            kalys_price = float(product[5]) if product[5] else None
            ileycom_price = float(product[6]) if product[6] else None
            sougui_price = float(product[3]) if product[3] else 0.0
            
            # Calculer le prix concurrent moyen
            competitor_prices = [p for p in [kalys_price, ileycom_price] if p is not None]
            avg_competitor_price = sum(competitor_prices) / len(competitor_prices) if competitor_prices else None
            
            # Déterminer la position concurrentielle
            if avg_competitor_price:
                if sougui_price < avg_competitor_price:
                    position = "Cheaper"
                elif sougui_price < avg_competitor_price * 1.1:
                    position = "Competitive"
                else:
                    position = "More_Expensive"
            else:
                position = "No_Competition"
            
            products_list.append({
                'id': int(product[0]),
                'reference': product[1],
                'name': product[2],
                'sougui_price': round(sougui_price, 2),
                'kalys_price': round(kalys_price, 2) if kalys_price else None,
                'ileycom_price': round(ileycom_price, 2) if ileycom_price else None,
                'avg_competitor_price': round(avg_competitor_price, 2) if avg_competitor_price else None,
                'position': position,
                'in_stock': int(product[4]) if product[4] else 0
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'products': products_list,
            'count': len(products_list),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except pyodbc.Error as e:
        return jsonify({
            'error': 'Erreur de connexion au Data Warehouse',
            'details': str(e)
        }), 500
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/health', methods=['GET'])
def health_check():
    """
    Vérification de l'état du service ML
    """
    return jsonify({
        'status': 'healthy',
        'service': 'ML Prediction Service',
        'timestamp': datetime.now().isoformat()
    }), 200


# ============================================================================
# IYADH - Classification des Fournisseurs
# ============================================================================

@ml_bp.route('/iyadh/suppliers', methods=['GET'])
@jwt_required()
def iyadh_get_suppliers():
    """
    Récupère la liste des fournisseurs avec leurs métriques
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Connexion au DWH
        conn = get_dwh_connection()
        cursor = conn.cursor()
        
        # Requête pour récupérer les fournisseurs avec métriques brutes
        suppliers_query = """
            SELECT 
                f.id_fournisseur,
                f.nom_fournisseur,
                f.matricule_fiscal,
                f.telephone,
                COUNT(DISTINCT fa.num_facture) as nb_factures,
                COUNT(DISTINCT fa.id_produit) as nb_produits,
                SUM(fa.montant_ht_facture) as montant_total_ht,
                SUM(fa.reste_du) as total_reste_du,
                COUNT(DISTINCT d.Annee * 100 + d.Mois) as nb_mois_actifs,
                DATEDIFF(DAY, MAX(d.Full_Date), GETDATE()) as jours_depuis_dernier_achat
            FROM dbo.Dim_Fournisseur f
            LEFT JOIN dbo.Fact_Achat fa ON f.id_fournisseur = fa.id_fournisseur
            LEFT JOIN dbo.Dim_Date d ON fa.date_key = d.Date_Key
            GROUP BY f.id_fournisseur, f.nom_fournisseur, f.matricule_fiscal, f.telephone
            HAVING COUNT(DISTINCT fa.num_facture) > 0
            ORDER BY SUM(fa.montant_ht_facture) DESC
        """
        
        cursor.execute(suppliers_query)
        suppliers = cursor.fetchall()
        
        # Calculer les max pour normalisation
        raw_data = []
        for s in suppliers:
            raw_data.append({
                'id': int(s[0]),
                'nom': s[1],
                'matricule_fiscal': s[2],
                'telephone': s[3],
                'nb_factures': int(s[4]) if s[4] else 0,
                'nb_produits': int(s[5]) if s[5] else 0,
                'montant_total_ht': float(s[6]) if s[6] else 0.0,
                'total_reste_du': float(s[7]) if s[7] else 0.0,
                'nb_mois_actifs': int(s[8]) if s[8] else 0,
                'jours_depuis_dernier_achat': int(s[9]) if s[9] else 999
            })
        
        # Taux de fiabilité composite (0-100) basé sur des métriques qui varient
        max_mois = max((r['nb_mois_actifs'] for r in raw_data), default=1) or 1
        max_montant = max((r['montant_total_ht'] for r in raw_data), default=1) or 1
        max_produits = max((r['nb_produits'] for r in raw_data), default=1) or 1
        
        for r in raw_data:
            # Régularité (35%): mois actifs / max mois
            regularity = min(r['nb_mois_actifs'] / max_mois, 1.0) * 100 * 0.35
            # Récence (30%): plus récent = meilleur
            recency = max(0, 100 - r['jours_depuis_dernier_achat'] / 3.65) * 0.30
            # Volume (20%): montant relatif au max
            volume = min(r['montant_total_ht'] / max_montant, 1.0) * 100 * 0.20
            # Diversité (15%): nombre de produits
            diversity = min(r['nb_produits'] / max_produits, 1.0) * 100 * 0.15
            
            r['taux_paiement'] = round(regularity + recency + volume + diversity, 1)
            r['montant_total_ht'] = round(r['montant_total_ht'], 2)
            r['total_reste_du'] = round(r['total_reste_du'], 2)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'suppliers': raw_data,
            'count': len(raw_data),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except pyodbc.Error as e:
        return jsonify({
            'error': 'Erreur de connexion au Data Warehouse',
            'details': str(e)
        }), 500
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/iyadh/classify-supplier', methods=['POST'])
@jwt_required()
def iyadh_classify_supplier():
    """
    Segmente un fournisseur: En Risque (0), Standard (1), Clé (2)
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        supplier_id = data.get('supplier_id')
        if not supplier_id:
            return jsonify({'error': 'supplier_id est requis'}), 400
        
        lang = data.get('lang', 'fr')
        
        # Charger le modèle
        model_path = 'ml_models/Iyadh/supplier_classifier.pkl'
        scaler_path = 'ml_models/Iyadh/supplier_scaler.pkl'
        features_path = 'ml_models/Iyadh/feature_columns.pkl'
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        feature_columns = joblib.load(features_path)
        
        # Connexion au DWH pour récupérer les features du fournisseur
        conn = get_dwh_connection()
        cursor = conn.cursor()
        
        # Requête pour extraire les features
        supplier_query = """
            SELECT 
                f.id_fournisseur,
                f.nom_fournisseur,
                f.matricule_fiscal,
                f.telephone,
                COUNT(DISTINCT fa.num_facture) as nb_factures,
                COUNT(DISTINCT fa.id_produit) as nb_produits_differents,
                SUM(fa.quantite) as quantite_totale,
                AVG(fa.quantite) as quantite_moyenne,
                SUM(fa.montant_ht_facture) as montant_total_ht,
                AVG(fa.montant_ht_facture) as montant_moyen_ht,
                SUM(fa.montant_ttc_facture) as montant_total_ttc,
                SUM(fa.reste_du) as total_reste_du,
                COUNT(DISTINCT d.Annee * 100 + d.Mois) as nb_mois_actifs,
                DATEDIFF(DAY, MAX(d.Full_Date), GETDATE()) as jours_depuis_dernier_achat,
                AVG(fa.montant_ligne) as montant_moyen_ligne
            FROM dbo.Dim_Fournisseur f
            LEFT JOIN dbo.Fact_Achat fa ON f.id_fournisseur = fa.id_fournisseur
            LEFT JOIN dbo.Dim_Date d ON fa.date_key = d.Date_Key
            WHERE f.id_fournisseur = ?
            GROUP BY f.id_fournisseur, f.nom_fournisseur, f.matricule_fiscal, f.telephone
        """
        
        cursor.execute(supplier_query, (supplier_id,))
        supplier_data = cursor.fetchone()
        
        if not supplier_data:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Fournisseur non trouvé'}), 404
        
        # Récupérer les max pour normalisation du taux de fiabilité
        max_query = """
            SELECT 
                MAX(sub.nb_mois),
                MAX(sub.montant),
                MAX(sub.nb_prod)
            FROM (
                SELECT 
                    COUNT(DISTINCT d.Annee * 100 + d.Mois) as nb_mois,
                    SUM(fa.montant_ht_facture) as montant,
                    COUNT(DISTINCT fa.id_produit) as nb_prod
                FROM dbo.Dim_Fournisseur f
                LEFT JOIN dbo.Fact_Achat fa ON f.id_fournisseur = fa.id_fournisseur
                LEFT JOIN dbo.Dim_Date d ON fa.date_key = d.Date_Key
                GROUP BY f.id_fournisseur
                HAVING COUNT(DISTINCT fa.num_facture) > 0
            ) sub
        """
        cursor.execute(max_query)
        max_row = cursor.fetchone()
        max_mois = float(max_row[0]) if max_row and max_row[0] else 1.0
        max_montant = float(max_row[1]) if max_row and max_row[1] else 1.0
        max_produits = float(max_row[2]) if max_row and max_row[2] else 1.0
        if max_mois == 0: max_mois = 1.0
        if max_montant == 0: max_montant = 1.0
        if max_produits == 0: max_produits = 1.0
        
        # Extraire les features brutes
        nb_mois_actifs = float(supplier_data[12]) if supplier_data[12] else 0.0
        jours_depuis_dernier_achat = float(supplier_data[13]) if supplier_data[13] else 999.0
        montant_total_ht = float(supplier_data[8]) if supplier_data[8] else 0.0
        nb_produits = float(supplier_data[5]) if supplier_data[5] else 0.0
        
        # Calcul du taux de fiabilité composite (0-100)
        regularity = min(nb_mois_actifs / max_mois, 1.0) * 100 * 0.35
        recency = max(0, 100 - jours_depuis_dernier_achat / 3.65) * 0.30
        volume = min(montant_total_ht / max_montant, 1.0) * 100 * 0.20
        diversity = min(nb_produits / max_produits, 1.0) * 100 * 0.15
        taux_paiement = round(regularity + recency + volume + diversity, 1)
        
        features = {
            'nb_factures': float(supplier_data[4]) if supplier_data[4] else 0.0,
            'nb_produits_differents': float(supplier_data[5]) if supplier_data[5] else 0.0,
            'quantite_totale': float(supplier_data[6]) if supplier_data[6] else 0.0,
            'quantite_moyenne': float(supplier_data[7]) if supplier_data[7] else 0.0,
            'montant_total_ht': montant_total_ht,
            'montant_moyen_ht': float(supplier_data[9]) if supplier_data[9] else 0.0,
            'total_reste_du': float(supplier_data[11]) if supplier_data[11] else 0.0,
            'taux_paiement': taux_paiement,
            'nb_mois_actifs': nb_mois_actifs,
            'jours_depuis_dernier_achat': jours_depuis_dernier_achat,
            'montant_moyen_ligne': float(supplier_data[14]) if supplier_data[14] else 0.0
        }
        
        # Préparer les features dans le bon ordre
        X = [features[col] for col in feature_columns]
        
        # Normaliser et prédire
        model_classes = list(getattr(model, 'classes_', []))
        if len(model_classes) > 1:
            X_scaled = scaler.transform([X])
            prediction = int(model.predict(X_scaled)[0])
            proba = model.predict_proba(X_scaled)[0]
            class_index = model_classes.index(prediction)
            probability = float(proba[class_index]) * 100
        else:
            # Fallback score-based segmentation when the classifier is invalid or single-class
            score = (
                min(nb_mois_actifs / max_mois, 1.0) * 100 * 0.35 +
                max(0, 100 - jours_depuis_dernier_achat / 3.65) * 0.30 +
                min(montant_total_ht / max_montant, 1.0) * 100 * 0.20 +
                min(nb_produits / max_produits, 1.0) * 100 * 0.15
            )
            if score >= 65:
                prediction = 2
            elif score >= 40:
                prediction = 1
            else:
                prediction = 0
            probability = min(max(score, 0.0), 100.0)
            print('WARNING: supplier classifier model invalid; using fallback score segmentation')

        # Si l'ancien modèle binaire est chargé, conserver la logique 0=En Risque / 1=Standard
        if len(model_classes) == 2 and set(model_classes) == {0, 1}:
            prediction = 0 if prediction == 0 else 1
        
        # Labels par segment: 0=En Risque, 1=Standard, 2=Clé
        segment_labels_fr = {0: 'En Risque', 1: 'Standard', 2: 'Clé'}
        segment_labels_en = {0: 'At Risk', 1: 'Standard', 2: 'Key'}
        segment_labels = segment_labels_fr if lang == 'fr' else segment_labels_en
        prediction_label = segment_labels.get(prediction, 'Inconnu')
        
        # Déterminer le niveau de confiance
        if probability >= 80:
            confidence_level = "Très Élevée" if lang == 'fr' else "Very High"
        elif probability >= 60:
            confidence_level = "Élevée" if lang == 'fr' else "High"
        elif probability >= 40:
            confidence_level = "Moyenne" if lang == 'fr' else "Medium"
        else:
            confidence_level = "Faible" if lang == 'fr' else "Low"
        
        # Analyse détaillée
        strengths = []
        weaknesses = []
        
        taux_paiement = features['taux_paiement']  # déjà en %
        if taux_paiement >= 80:
            strengths.append(f"Excellent taux de paiement ({taux_paiement:.1f}%)" if lang == 'fr' else f"Excellent payment rate ({taux_paiement:.1f}%)")
        elif taux_paiement < 50:
            weaknesses.append(f"Taux de paiement faible ({taux_paiement:.1f}%)" if lang == 'fr' else f"Low payment rate ({taux_paiement:.1f}%)")
        
        if features['nb_mois_actifs'] >= 6:
            strengths.append(f"Fournisseur régulier ({int(features['nb_mois_actifs'])} mois actifs)" if lang == 'fr' else f"Regular supplier ({int(features['nb_mois_actifs'])} active months)")
        elif features['nb_mois_actifs'] < 3:
            weaknesses.append(f"Activité irrégulière ({int(features['nb_mois_actifs'])} mois actifs)" if lang == 'fr' else f"Irregular activity ({int(features['nb_mois_actifs'])} active months)")
        
        if features['jours_depuis_dernier_achat'] < 90:
            strengths.append("Activité récente" if lang == 'fr' else "Recent activity")
        elif features['jours_depuis_dernier_achat'] > 180:
            weaknesses.append(f"Inactif depuis {int(features['jours_depuis_dernier_achat'])} jours" if lang == 'fr' else f"Inactive for {int(features['jours_depuis_dernier_achat'])} days")
        
        if features['montant_total_ht'] > 10000:
            strengths.append(f"Volume d'affaires important ({features['montant_total_ht']:.0f} TND)" if lang == 'fr' else f"Significant business volume ({features['montant_total_ht']:.0f} TND)")
        
        # Recommandation par segment
        if prediction == 2:  # Clé
            if lang == 'fr':
                recommendation_text = f"🔑 Fournisseur CLÉ — Partenaire stratégique fiable ({probability:.1f}%). "
                if strengths:
                    recommendation_text += "Points forts: " + ", ".join(strengths[:2])
            else:
                recommendation_text = f"🔑 KEY supplier — Reliable strategic partner ({probability:.1f}%). "
                if strengths:
                    recommendation_text += "Strengths: " + ", ".join(strengths[:2])
        elif prediction == 1:  # Standard
            if lang == 'fr':
                recommendation_text = f"📋 Fournisseur STANDARD — Performance acceptable ({probability:.1f}%). "
                if weaknesses:
                    recommendation_text += "Points d'amélioration: " + ", ".join(weaknesses[:2])
            else:
                recommendation_text = f"📋 STANDARD supplier — Acceptable performance ({probability:.1f}%). "
                if weaknesses:
                    recommendation_text += "Areas for improvement: " + ", ".join(weaknesses[:2])
        else:  # En Risque
            if lang == 'fr':
                recommendation_text = f"⚠️ Fournisseur EN RISQUE — Surveillance requise ({probability:.1f}%). "
                if weaknesses:
                    recommendation_text += "Risques identifiés: " + ", ".join(weaknesses[:2])
            else:
                recommendation_text = f"⚠️ AT RISK supplier — Monitoring required ({probability:.1f}%). "
                if weaknesses:
                    recommendation_text += "Identified risks: " + ", ".join(weaknesses[:2])
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'supplier_id': supplier_id,
            'supplier_name': supplier_data[1],
            'segment': prediction,
            'prediction_label': prediction_label,
            'probability': round(probability, 1),
            'confidence_level': confidence_level,
            'features_used': {
                'nb_factures': int(features['nb_factures']),
                'nb_produits_differents': int(features['nb_produits_differents']),
                'montant_total_ht': round(features['montant_total_ht'], 2),
                'taux_paiement': round(features['taux_paiement'], 1),
                'nb_mois_actifs': int(features['nb_mois_actifs']),
                'jours_depuis_dernier_achat': int(features['jours_depuis_dernier_achat'])
            },
            'analysis': {
                'strengths': strengths,
                'weaknesses': weaknesses,
                'recommendation': recommendation_text
            },
            'model': 'Random Forest Supplier Segmenter (Iyadh)',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except FileNotFoundError:
        return jsonify({'error': 'Modèle non trouvé. Veuillez entraîner le modèle d\'abord.'}), 404
    except pyodbc.Error as e:
        return jsonify({
            'error': 'Erreur de connexion au Data Warehouse',
            'details': str(e)
        }), 500
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/iyadh/train-supplier-model', methods=['POST'])
@jwt_required()
def iyadh_train_supplier_model():
    """
    Entraîne le modèle de segmentation des fournisseurs: En Risque (0), Standard (1), Clé (2)
    """
    try:
        current_user_id = get_jwt_identity()
        
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import classification_report
        
        # Connexion au DWH
        conn = get_dwh_connection()
        
        # Extraction des features fournisseurs
        query = """
            SELECT 
                f.id_fournisseur,
                f.nom_fournisseur,
                f.matricule_fiscal,
                f.telephone,
                COUNT(DISTINCT fa.num_facture) as nb_factures,
                COUNT(DISTINCT fa.id_produit) as nb_produits_differents,
                SUM(fa.quantite) as quantite_totale,
                AVG(fa.quantite) as quantite_moyenne,
                SUM(fa.montant_ht_facture) as montant_total_ht,
                AVG(fa.montant_ht_facture) as montant_moyen_ht,
                SUM(fa.montant_ttc_facture) as montant_total_ttc,
                SUM(fa.reste_du) as total_reste_du,
                COUNT(DISTINCT d.Annee * 100 + d.Mois) as nb_mois_actifs,
                DATEDIFF(DAY, MAX(d.Full_Date), GETDATE()) as jours_depuis_dernier_achat,
                AVG(fa.montant_ligne) as montant_moyen_ligne,
                STDEV(fa.montant_ht_facture) as ecart_type_montant
            FROM dbo.Dim_Fournisseur f
            LEFT JOIN dbo.Fact_Achat fa ON f.id_fournisseur = fa.id_fournisseur
            LEFT JOIN dbo.Dim_Date d ON fa.date_key = d.Date_Key
            GROUP BY f.id_fournisseur, f.nom_fournisseur, f.matricule_fiscal, f.telephone
            HAVING COUNT(DISTINCT fa.num_facture) > 0
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        if len(df) == 0:
            return jsonify({'error': 'Aucune donnée fournisseur disponible pour l\'entraînement'}), 400
        
        # Calcul du taux de fiabilité composite (0-100) en Python
        max_mois = df['nb_mois_actifs'].max() if df['nb_mois_actifs'].max() > 0 else 1
        max_montant = df['montant_total_ht'].max() if df['montant_total_ht'].max() > 0 else 1
        max_produits = df['nb_produits_differents'].max() if df['nb_produits_differents'].max() > 0 else 1
        
        df['taux_paiement'] = (
            (df['nb_mois_actifs'].clip(0, max_mois) / max_mois * 100 * 0.35) +
            (100 - df['jours_depuis_dernier_achat'].clip(0, 365) / 365 * 100) * 0.30 +
            (df['montant_total_ht'].clip(0, max_montant) / max_montant * 100 * 0.20) +
            (df['nb_produits_differents'].clip(0, max_produits) / max_produits * 100 * 0.15)
        ).round(1)
        
        # Création des labels de segmentation: 0=En Risque, 1=Standard, 2=Clé
        # Score composite basé sur les métriques métier
        median_montant = df['montant_total_ht'].median()
        
        # Calcul du score composite (0-100)
        df['score'] = 0.0
        # Taux de fiabilité (poids 35%)
        df['score'] += df['taux_paiement'].clip(0, 100) * 0.35
        # Régularité (poids 25%): plus de mois actifs = mieux
        df['score'] += (df['nb_mois_actifs'].clip(0, 12) / 12 * 100) * 0.25
        # Récence (poids 20%): plus récent = mieux (0 jours = 100, 365+ jours = 0)
        df['score'] += (100 - df['jours_depuis_dernier_achat'].clip(0, 365) / 365 * 100) * 0.20
        # Volume (poids 20%): au-dessus de la médiane = 100, en dessous proportionnel
        df['score'] += (df['montant_total_ht'] / median_montant * 100).clip(0, 100) * 0.20
        
        # Segmentation basée sur la distribution des scores
        q33 = df['score'].quantile(0.33)
        q66 = df['score'].quantile(0.66)
        df['segment'] = 0  # En Risque par défaut
        df.loc[df['score'] >= q33, 'segment'] = 1  # Standard
        df.loc[df['score'] >= q66, 'segment'] = 2  # Clé
        
        # Features
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
        
        df[feature_columns] = df[feature_columns].fillna(0)
        
        X = df[feature_columns]
        y = df['segment']
        
        # Vérifier qu'on a au moins 2 classes
        unique_classes = y.nunique()
        if unique_classes < 2:
            # Ajuster les seuils si nécessaire
            q33 = df['score'].quantile(0.33)
            q66 = df['score'].quantile(0.66)
            df['segment'] = 0
            df.loc[df['score'] >= q33, 'segment'] = 1
            df.loc[df['score'] >= q66, 'segment'] = 2
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
        accuracy = float(model.score(X_test_scaled, y_test))
        
        n_risque = int((df['segment'] == 0).sum())
        n_standard = int((df['segment'] == 1).sum())
        n_cle = int((df['segment'] == 2).sum())
        
        # Sauvegarde du modèle
        os.makedirs('ml_models/Iyadh', exist_ok=True)
        
        joblib.dump(model, 'ml_models/Iyadh/supplier_classifier.pkl')
        joblib.dump(scaler, 'ml_models/Iyadh/supplier_scaler.pkl')
        joblib.dump(feature_columns, 'ml_models/Iyadh/feature_columns.pkl')
        
        metadata = {
            'model_type': 'RandomForestClassifier',
            'n_features': len(feature_columns),
            'feature_names': feature_columns,
            'trained_date': datetime.now().isoformat(),
            'accuracy': accuracy,
            'n_suppliers': len(df),
            'n_risque': n_risque,
            'n_standard': n_standard,
            'n_cle': n_cle,
            'description': 'Segmentation des fournisseurs (En Risque/Standard/Clé)'
        }
        joblib.dump(metadata, 'ml_models/Iyadh/model_metadata.pkl')
        
        return jsonify({
            'message': 'Modèle entraîné avec succès',
            'accuracy': round(accuracy, 3),
            'n_suppliers': len(df),
            'n_risque': n_risque,
            'n_standard': n_standard,
            'n_cle': n_cle,
            'feature_importance': dict(zip(feature_columns, [round(float(fi), 3) for fi in model.feature_importances_])),
            'trained_date': datetime.now().isoformat()
        }), 200
        
    except pyodbc.Error as e:
        return jsonify({
            'error': 'Erreur de connexion au Data Warehouse',
            'details': str(e)
        }), 500
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

