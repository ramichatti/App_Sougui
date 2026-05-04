"""
Script pour inspecter le contenu du modèle de segmentation
"""
import pickle
import joblib
import os

model_path = 'ml_models/Balkis/segmentation_clients.pkl'

print("=" * 70)
print("INSPECTION DU MODÈLE DE SEGMENTATION")
print("=" * 70)

# Vérifier si le fichier existe
if not os.path.exists(model_path):
    print(f"❌ Fichier non trouvé: {model_path}")
    exit(1)

print(f"✅ Fichier trouvé: {model_path}")
print(f"Taille du fichier: {os.path.getsize(model_path)} bytes")

# Essayer de charger avec joblib
print("\n--- Test avec joblib ---")
try:
    model_joblib = joblib.load(model_path)
    print(f"✅ Chargement joblib réussi")
    print(f"Type: {type(model_joblib)}")
    print(f"Contenu: {model_joblib}")
    
    if hasattr(model_joblib, 'predict'):
        print("✅ Méthode 'predict' disponible")
    else:
        print("❌ Méthode 'predict' non disponible")
        
    if isinstance(model_joblib, dict):
        print("\n📋 Clés du dictionnaire:")
        for key, value in model_joblib.items():
            print(f"  - {key}: {type(value)}")
            if hasattr(value, 'predict'):
                print(f"    ✅ {key} a une méthode 'predict'")
            else:
                print(f"    ❌ {key} n'a pas de méthode 'predict'")
                
except Exception as e:
    print(f"❌ Erreur joblib: {str(e)}")

# Essayer de charger avec pickle
print("\n--- Test avec pickle ---")
try:
    with open(model_path, 'rb') as f:
        model_pickle = pickle.load(f)
    print(f"✅ Chargement pickle réussi")
    print(f"Type: {type(model_pickle)}")
    print(f"Contenu: {model_pickle}")
    
    if hasattr(model_pickle, 'predict'):
        print("✅ Méthode 'predict' disponible")
    else:
        print("❌ Méthode 'predict' non disponible")
        
    if isinstance(model_pickle, dict):
        print("\n📋 Clés du dictionnaire:")
        for key, value in model_pickle.items():
            print(f"  - {key}: {type(value)}")
            if hasattr(value, 'predict'):
                print(f"    ✅ {key} a une méthode 'predict'")
            else:
                print(f"    ❌ {key} n'a pas de méthode 'predict'")
                
except Exception as e:
    print(f"❌ Erreur pickle: {str(e)}")

# Vérifier les autres modèles de Balkis pour comparaison
print("\n" + "=" * 70)
print("COMPARAISON AVEC D'AUTRES MODÈLES BALKIS")
print("=" * 70)

other_models = [
    'ml_models/Balkis/rf_classifier_prod.pkl',
    'ml_models/Balkis/kmeans_clustering_prod.pkl'
]

for other_model_path in other_models:
    if os.path.exists(other_model_path):
        print(f"\n--- {other_model_path} ---")
        try:
            other_model = joblib.load(other_model_path)
            print(f"Type: {type(other_model)}")
            if hasattr(other_model, 'predict'):
                print("✅ Méthode 'predict' disponible")
            else:
                print("❌ Méthode 'predict' non disponible")
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
    else:
        print(f"❌ Fichier non trouvé: {other_model_path}")

print("\n" + "=" * 70)
print("RECOMMANDATIONS")
print("=" * 70)

print("""
Si le modèle est un dictionnaire, il peut contenir:
1. Le modèle KMeans sous une clé spécifique (ex: 'model', 'kmeans', 'classifier')
2. Des métadonnées supplémentaires (scaler, encoders, etc.)

Solutions possibles:
1. Identifier la bonne clé qui contient le modèle
2. Modifier le code pour extraire le modèle du dictionnaire
3. Re-sauvegarder le modèle correctement si nécessaire
""")