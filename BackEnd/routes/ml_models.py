from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import pickle
import numpy as np
import pandas as pd
import os
from models import User

ml_models_bp = Blueprint('ml_models', __name__, url_prefix='/api/ml-models')

# Path to Balkis models
BALKIS_MODELS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml_models', 'Balkis')


def _require_admin():
    """Helper to check if user is admin"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return None, (jsonify({'error': 'Admin access required'}), 403)
    return user, None


@ml_models_bp.route('/balkis/best-seller', methods=['POST'])
@jwt_required()
def predict_best_seller():
    """Best Seller prediction"""
    try:
        _, err = _require_admin()
        if err:
            return err

        data = request.get_json()
        
        # Validate input with real feature names
        required_fields = ['prix_moyen', 'quantite_moyenne', 'nombre_commandes', 
                          'taux_reduction', 'velocite_ventes', 'categorie_prix']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields', 'required': required_fields}), 400

        # Load model
        model_path = os.path.join(BALKIS_MODELS_PATH, 'best_seller_simplifie.pkl')
        if not os.path.exists(model_path):
            return jsonify({'error': 'Model file not found'}), 404

        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
                # The pickle file contains a dictionary with the model
                if isinstance(model_data, dict) and 'model' in model_data:
                    model = model_data['model']
                else:
                    model = model_data
        except Exception as load_error:
            return jsonify({'error': 'Failed to load model', 'details': str(load_error)}), 500

        # Prepare input
        try:
            features = np.array([[
                float(data['prix_moyen']),
                float(data['quantite_moyenne']),
                float(data['nombre_commandes']),
                float(data['taux_reduction']),
                float(data['velocite_ventes']),
                int(data['categorie_prix'])
            ]])
        except Exception as prep_error:
            return jsonify({'error': 'Failed to prepare features', 'details': str(prep_error)}), 400

        # Predict
        try:
            prediction = float(model.predict(features)[0])
        except Exception as pred_error:
            return jsonify({'error': 'Prediction failed', 'details': str(pred_error)}), 500
        
        # Calculate best seller score based on prediction
        score = min(prediction / 30.0, 1.0)  # Normalize to 0-1
        
        # Determine best seller status
        if score > 0.7:
            status = '⭐⭐⭐ OUI'
            status_class = 'excellent'
        elif score > 0.5:
            status = '⭐⭐ Probable'
            status_class = 'good'
        elif score > 0.3:
            status = '⭐ Possible'
            status_class = 'medium'
        else:
            status = 'Non'
            status_class = 'low'

        return jsonify({
            'prediction': round(prediction, 1),
            'score': round(score, 3),
            'status': status,
            'status_class': status_class,
            'input_features': {
                'prix_moyen': features[0][0],
                'quantite_moyenne': features[0][1],
                'nombre_commandes': features[0][2],
                'taux_reduction': features[0][3],
                'velocite_ventes': features[0][4],
                'categorie_prix': int(features[0][5])
            }
        }), 200

    except ValueError as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Invalid input values', 'details': str(e)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Prediction failed', 'details': str(e)}), 500


@ml_models_bp.route('/balkis/kmeans', methods=['POST'])
@jwt_required()
def predict_kmeans():
    """K-Means Clustering prediction - Segmentation clients"""
    try:
        _, err = _require_admin()
        if err:
            return err

        data = request.get_json()
        
        # Real feature names from the segmentation model
        required_fields = ['recency', 'frequency', 'monetary', 'panier_moyen', 
                          'quantite_totale', 'taux_reduction', 'produits_par_commande']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields', 'required': required_fields}), 400

        # Load model
        model_path = os.path.join(BALKIS_MODELS_PATH, 'segmentation_clients.pkl')
        if not os.path.exists(model_path):
            return jsonify({'error': 'Model file not found'}), 404

        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
                # Extract components from the pipeline
                model = model_data['model']
                scaler = model_data.get('scaler')
                pca = model_data.get('pca')
                cluster_names = model_data.get('cluster_names', {})
                features = model_data.get('features', [])
        except Exception as load_error:
            return jsonify({'error': 'Failed to load model', 'details': str(load_error)}), 500

        # Prepare input
        try:
            # Use the exact feature names from the model training
            feature_names = ['Recency', 'Frequency', 'Monetary', 'Panier_Moyen', 
                           'Quantité_Totale', 'Taux_Réduction', 'Produits_Par_Commande']
            
            # Create DataFrame with proper column names
            features_df = pd.DataFrame([[
                float(data['recency']),
                float(data['frequency']),
                float(data['monetary']),
                float(data['panier_moyen']),
                float(data['quantite_totale']),
                float(data['taux_reduction']),
                float(data['produits_par_commande'])
            ]], columns=feature_names)
            
            # Apply preprocessing pipeline - KMeans was trained on scaled data, NOT PCA data
            if scaler:
                features_processed = scaler.transform(features_df)
            else:
                features_processed = features_df.values
                
        except Exception as prep_error:
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Failed to prepare features', 'details': str(prep_error)}), 400

        # Predict
        try:
            cluster = int(model.predict(features_processed)[0])
        except Exception as pred_error:
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Prediction failed', 'details': str(pred_error)}), 500
        
        # Get cluster name
        cluster_name = cluster_names.get(cluster, f'Cluster {cluster}')
        
        # Get cluster centers if available
        cluster_centers = None
        if hasattr(model, 'cluster_centers_'):
            cluster_centers = model.cluster_centers_.tolist()

        # Calculate distance to cluster center
        distance = None
        if cluster_centers:
            center = np.array(cluster_centers[cluster])
            distance = float(np.linalg.norm(features_processed[0] - center))

        return jsonify({
            'cluster': cluster,
            'cluster_name': cluster_name,
            'cluster_centers': cluster_centers,
            'distance_to_center': distance,
            'n_clusters': len(cluster_centers) if cluster_centers else model_data.get('optimal_k'),
            'input_features': {
                'recency': features_df.iloc[0, 0],
                'frequency': features_df.iloc[0, 1],
                'monetary': features_df.iloc[0, 2],
                'panier_moyen': features_df.iloc[0, 3],
                'quantite_totale': features_df.iloc[0, 4],
                'taux_reduction': features_df.iloc[0, 5],
                'produits_par_commande': features_df.iloc[0, 6]
            },
            'feature_names': features
        }), 200

    except ValueError as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Invalid input values', 'details': str(e)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Prediction failed', 'details': str(e)}), 500


@ml_models_bp.route('/balkis/models-info', methods=['GET'])
@jwt_required()
def get_models_info():
    """Get information about available Balkis models"""
    try:
        _, err = _require_admin()
        if err:
            return err

        models_info = []

        # Check K-Means model
        kmeans_path = os.path.join(BALKIS_MODELS_PATH, 'kmeans_clustering_prod.pkl')
        if os.path.exists(kmeans_path):
            try:
                with open(kmeans_path, 'rb') as f:
                    kmeans_model = pickle.load(f)
                
                models_info.append({
                    'name': 'K-Means Clustering',
                    'type': 'clustering',
                    'file': 'kmeans_clustering_prod.pkl',
                    'status': 'ready',
                    'n_clusters': int(kmeans_model.n_clusters) if hasattr(kmeans_model, 'n_clusters') else None,
                    'features_required': 4,
                    'description': 'Modèle de clustering K-Means pour segmentation'
                })
            except Exception as e:
                models_info.append({
                    'name': 'K-Means Clustering',
                    'type': 'clustering',
                    'file': 'kmeans_clustering_prod.pkl',
                    'status': 'error',
                    'error': str(e)
                })

        # Check Random Forest model
        rf_path = os.path.join(BALKIS_MODELS_PATH, 'rf_classifier_prod.pkl')
        if os.path.exists(rf_path):
            try:
                with open(rf_path, 'rb') as f:
                    rf_model = pickle.load(f)
                
                models_info.append({
                    'name': 'Random Forest Classifier',
                    'type': 'classification',
                    'file': 'rf_classifier_prod.pkl',
                    'status': 'ready',
                    'n_classes': int(rf_model.n_classes_) if hasattr(rf_model, 'n_classes_') else None,
                    'n_estimators': int(rf_model.n_estimators) if hasattr(rf_model, 'n_estimators') else None,
                    'features_required': 5,
                    'description': 'Modèle de classification Random Forest'
                })
            except Exception as e:
                models_info.append({
                    'name': 'Random Forest Classifier',
                    'type': 'classification',
                    'file': 'rf_classifier_prod.pkl',
                    'status': 'error',
                    'error': str(e)
                })

        return jsonify({'models': models_info}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get models info', 'details': str(e)}), 500
