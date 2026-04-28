# Sougui Backend - Flask API

Application décisionnelle pour l'entreprise Sougui (vente de produits artisanaux).

## Technologies
- Flask (Python)
- MySQL (via XAMPP)
- JWT Authentication
- Flask-Mail

## Installation

### 1. Prérequis
- Python 3.8+
- XAMPP (MySQL)

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Configuration XAMPP
1. Démarrer XAMPP
2. Lancer Apache et MySQL
3. Créer la base de données:
   - Ouvrir phpMyAdmin (http://localhost/phpmyadmin)
   - Créer une base de données nommée `sougui_db`

### 4. Configuration
1. Copier `.env.example` vers `.env`
2. Modifier les paramètres dans `.env`:
   - Configuration email (Gmail recommandé)
   - Clés secrètes

### 5. Initialiser la base de données
```bash
python init_db.py
```

### 6. Lancer l'application
```bash
python app.py
```

L'API sera disponible sur: http://localhost:5000

## Utilisateurs par défaut
- **Admin**: admin@sougui.com / admin123
- **Directeur Vente**: vente@sougui.com / vente123
- **Directeur Achat**: achat@sougui.com / achat123

## API Endpoints

### Authentication
- `POST /api/auth/login` - Connexion
- `POST /api/auth/forgot-password` - Demander code de réinitialisation
- `POST /api/auth/verify-reset-code` - Vérifier le code
- `POST /api/auth/reset-password` - Réinitialiser le mot de passe
- `GET /api/auth/me` - Obtenir l'utilisateur connecté

### Admin (Admin uniquement)
- `GET /api/admin/users` - Liste des utilisateurs
- `POST /api/admin/users` - Créer un utilisateur
- `PUT /api/admin/users/:id` - Modifier un utilisateur
- `DELETE /api/admin/users/:id` - Supprimer un utilisateur
- `GET /api/admin/dashboards` - Liste des dashboards
- `POST /api/admin/dashboards` - Créer un dashboard
- `PUT /api/admin/dashboards/:id` - Modifier un dashboard
- `DELETE /api/admin/dashboards/:id` - Supprimer un dashboard

### Dashboard
- `GET /api/dashboard/my-dashboards` - Obtenir les dashboards de l'utilisateur connecté

## Configuration Email (Gmail)
1. Activer l'authentification à deux facteurs
2. Générer un mot de passe d'application
3. Utiliser ce mot de passe dans `.env`
