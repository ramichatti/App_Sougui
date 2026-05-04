from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import joblib
import os
import pandas as pd
import numpy as np

delivery_bp = Blueprint('delivery', __name__, url_prefix='/api/delivery')

# ============================================
# CHEMIN DES MODÈLES
# ============================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_PATH = os.path.join(BASE_DIR, 'ml_models', 'Mariem')

print("=" * 50)
print("🔧 Chargement des modèles Delivery...")
print(f"📁 Chemin: {MODELS_PATH}")

try:
    lr_model = joblib.load(os.path.join(MODELS_PATH, 'linear_regression_model.pkl'))
    print("✅ Régression Linéaire chargée")
    models_loaded = True
except Exception as e:
    print(f"❌ Erreur chargement: {e}")
    lr_model = None
    models_loaded = False

# ============================================
# PRÉDICTION COÛT
# ============================================
@delivery_bp.route('/predict/cout', methods=['POST'])
@jwt_required()
def predict_cout():
    try:
        data = request.get_json()
        distance = data.get('distance_km')
        
        if distance is None:
            return jsonify({'error': 'distance_km est requis'}), 400
        
        if lr_model is None:
            return jsonify({'error': 'Modèle non disponible'}), 503
        
        X = pd.DataFrame([[distance]], columns=['Distance_km'])
        prediction = lr_model.predict(X)[0]
        
        return jsonify({
            'success': True,
            'distance_km': distance,
            'cout_predit': round(prediction, 2),
            'unite': 'dt'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# CALCUL DE DISTANCE HAVERSINE
# ============================================
@delivery_bp.route('/distance', methods=['POST'])
@jwt_required()
def calculate_distance():
    try:
        data = request.get_json()
        lat1 = data.get('lat1')
        lon1 = data.get('lon1')
        lat2 = data.get('lat2')
        lon2 = data.get('lon2')
        
        if None in [lat1, lon1, lat2, lon2]:
            return jsonify({'error': 'lat1, lon1, lat2, lon2 sont requis'}), 400
        
        R = 6371
        lat1_rad = np.radians(lat1)
        lon1_rad = np.radians(lon1)
        lat2_rad = np.radians(lat2)
        lon2_rad = np.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        distance = R * c
        
        return jsonify({
            'success': True,
            'distance_km': round(distance, 2)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# SANTÉ DES MODÈLES
# ============================================
@delivery_bp.route('/health', methods=['GET'])
@jwt_required()
def health():
    return jsonify({
        'status': 'ok',
        'models_loaded': models_loaded
    }), 200