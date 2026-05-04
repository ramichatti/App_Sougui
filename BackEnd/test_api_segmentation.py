"""
Test de l'API de segmentation client
"""
import requests
import json
import sys
sys.path.append('.')

from app import app, db
from models import User, Role
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Créer un utilisateur admin pour les tests"""
    with app.app_context():
        # Vérifier si l'utilisateur admin existe
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            # Créer le rôle admin s'il n'existe pas
            admin_role = Role.query.filter_by(name='Admin').first()
            if not admin_role:
                admin_role = Role(name='Admin', description='Administrator')
                db.session.add(admin_role)
                db.session.commit()
            
            # Créer l'utilisateur admin
            admin_user = User(
                username='admin',
                email='admin@test.com',
                password_hash=generate_password_hash('admin123'),
                role_id=admin_role.id
            )
            db.session.add(admin_user)
            db.session.commit()
            print('✅ Utilisateur admin créé')
        else:
            print('✅ Utilisateur admin existe déjà')

def test_segmentation_api():
    """Tester l'API de segmentation"""
    # Créer l'utilisateur admin
    create_admin_user()
    
    # URLs
    login_url = 'http://localhost:5000/api/auth/login'
    segmentation_url = 'http://localhost:5000/api/ml/balkis/client-segmentation'
    
    # Données de login
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        # 1. Login pour obtenir le token
        print("\n1. Connexion...")
        login_response = requests.post(login_url, json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Erreur de login: {login_response.text}")
            return
        
        token = login_response.json()['access_token']
        print('✅ Token obtenu')
        
        # 2. Tester la segmentation globale
        print("\n2. Test de la segmentation globale...")
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(segmentation_url, json={}, headers=headers)
        
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ Segmentation réussie!')
            print(f'Total clients: {data.get("total_clients", 0)}')
            print(f'Nombre de clusters: {data.get("n_clusters", 0)}')
            print(f'Segments trouvés: {len(data.get("segment_stats", []))}')
            
            for stat in data.get('segment_stats', []):
                print(f'  - {stat["segment_name"]}: {stat["client_count"]} clients')
            
            # Afficher quelques clients
            clients = data.get('clients', [])
            if clients:
                print(f'\nPremiers clients:')
                for i, client in enumerate(clients[:5]):
                    print(f'  {i+1}. {client["client_name"]} - {client["segment_name"]} (CA: {client["ca_total"]} TND)')
        else:
            print(f'❌ Erreur: {response.text}')
            
        # 3. Tester la segmentation d'un client spécifique
        print("\n3. Test de la segmentation d'un client spécifique...")
        if response.status_code == 200:
            data = response.json()
            clients = data.get('clients', [])
            if clients:
                test_client_id = clients[0]['client_id']
                client_data = {'client_id': test_client_id}
                
                client_response = requests.post(segmentation_url, json=client_data, headers=headers)
                
                if client_response.status_code == 200:
                    client_result = client_response.json()
                    print(f'✅ Segmentation client réussie!')
                    print(f'Client: {client_result["client_name"]}')
                    print(f'Segment: {client_result["segment_name"]}')
                    print(f'Cluster: {client_result["cluster"]}')
                    print(f'Features utilisées:')
                    for feature, value in client_result.get('features_used', {}).items():
                        print(f'  - {feature}: {value}')
                else:
                    print(f'❌ Erreur segmentation client: {client_response.text}')
        
    except requests.exceptions.ConnectionError:
        print('❌ Erreur de connexion: Serveur Flask non démarré sur le port 5000')
    except Exception as e:
        print(f'❌ Erreur: {str(e)}')

if __name__ == '__main__':
    test_segmentation_api()