# 🏺 Sougui - Application Décisionnelle

Application décisionnelle pour l'entreprise Sougui (vente de produits artisanaux) avec dashboards Power BI intégrés.

## 📋 Caractéristiques

### Architecture
- **Backend**: Flask (Python) + MySQL
- **Frontend**: Angular 17 (Standalone)
- **Base de données**: MySQL via XAMPP
- **Thème**: Bleu et Blanc

### Fonctionnalités
- ✅ Authentification sécurisée (JWT)
- ✅ Mot de passe oublié avec code à expiration (15 minutes)
- ✅ 3 rôles utilisateurs:
  - **Admin (Founder)**: Accès complet + backoffice
  - **Directeur Vente**: Dashboard ventes
  - **Directeur Achat**: Dashboard achats
- ✅ Dashboards Power BI intégrés (iframe)
- ✅ Backoffice admin pour gérer:
  - Utilisateurs
  - Dashboards Power BI

## 🚀 Installation Complète

### Prérequis
1. **XAMPP** - Pour MySQL
2. **Python 3.8+**
3. **Node.js 18+** et npm
4. **Angular CLI**: `npm install -g @angular/cli`

### Étape 1: Configuration XAMPP
1. Installer et lancer XAMPP
2. Démarrer les services **Apache** et **MySQL**
3. Ouvrir phpMyAdmin: http://localhost/phpmyadmin
4. Créer une base de données nommée: `sougui_db`

### Étape 2: Backend Flask

```bash
# Naviguer vers le dossier backend
cd BackEnd

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Copier et configurer .env
copy .env.example .env
# Éditer .env avec vos paramètres (email, etc.)

# Initialiser la base de données
python init_db.py

# Lancer le serveur
python app.py
```

Le backend sera disponible sur: **http://localhost:5000**

### Étape 3: Frontend Angular

```bash
# Naviguer vers le dossier frontend
cd FrontEnd

# Installer les dépendances
npm install

# Lancer l'application
npm start
```

Le frontend sera disponible sur: **http://localhost:4200**

## 👥 Comptes par Défaut

Après l'initialisation de la base de données:

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| Admin | admin@sougui.com | admin123 |
| Directeur Vente | vente@sougui.com | vente123 |
| Directeur Achat | achat@sougui.com | achat123 |

## 📊 Configuration Power BI

1. Se connecter en tant qu'**Admin**
2. Aller dans **Administration** → **Dashboards**
3. Créer/Modifier les dashboards avec les URLs Power BI
4. Format URL Power BI: `https://app.powerbi.com/view?r=YOUR_REPORT_ID`

### Obtenir l'URL d'intégration Power BI:
1. Ouvrir votre rapport dans Power BI Service
2. Cliquer sur **Fichier** → **Incorporer le rapport** → **Site web ou portail**
3. Copier l'URL générée
4. Coller dans le champ "URL Power BI" de l'admin

## 📁 Structure du Projet

```
Dev/
├── BackEnd/                 # API Flask
│   ├── routes/             # Routes API
│   ├── models.py           # Modèles de données
│   ├── config.py           # Configuration
│   ├── app.py              # Application principale
│   ├── init_db.py          # Initialisation DB
│   └── requirements.txt    # Dépendances Python
│
└── FrontEnd/               # Application Angular
    ├── src/
    │   ├── app/
    │   │   ├── core/       # Services, Guards, Models
    │   │   └── features/   # Composants (Auth, Dashboard, Admin)
    │   ├── environments/   # Configuration
    │   └── styles.css      # Thème bleu/blanc
    └── package.json        # Dépendances Node
```

## 🎨 Thème Couleurs

- **Bleu Primaire**: #1e3a8a
- **Bleu Secondaire**: #3b82f6
- **Bleu Clair**: #60a5fa
- **Blanc**: #ffffff
- **Gris Clair**: #f3f4f6

## 🔧 Configuration Email (Mot de passe oublié)

Éditer `BackEnd/.env`:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=votre-email@gmail.com
MAIL_PASSWORD=votre-mot-de-passe-application
```

### Pour Gmail:
1. Activer l'authentification à deux facteurs
2. Générer un mot de passe d'application
3. Utiliser ce mot de passe dans `.env`

## 📝 API Endpoints

### Authentification
- `POST /api/auth/login` - Connexion
- `POST /api/auth/forgot-password` - Demander code
- `POST /api/auth/verify-reset-code` - Vérifier code
- `POST /api/auth/reset-password` - Réinitialiser
- `GET /api/auth/me` - Utilisateur connecté

### Dashboard
- `GET /api/dashboard/my-dashboards` - Mes dashboards

### Admin (Admin uniquement)
- `GET /api/admin/users` - Liste utilisateurs
- `POST /api/admin/users` - Créer utilisateur
- `PUT /api/admin/users/:id` - Modifier utilisateur
- `DELETE /api/admin/users/:id` - Supprimer utilisateur
- `GET /api/admin/dashboards` - Liste dashboards
- `POST /api/admin/dashboards` - Créer dashboard
- `PUT /api/admin/dashboards/:id` - Modifier dashboard
- `DELETE /api/admin/dashboards/:id` - Supprimer dashboard

## 🐛 Dépannage

### Backend ne démarre pas
- Vérifier que MySQL est démarré dans XAMPP
- Vérifier que la base `sougui_db` existe
- Vérifier les paramètres dans `.env`

### Frontend ne démarre pas
- Vérifier que Node.js est installé: `node --version`
- Réinstaller les dépendances: `npm install`
- Vérifier qu'Angular CLI est installé: `ng version`

### Erreur CORS
- Vérifier que le backend est lancé sur le port 5000
- Vérifier la configuration CORS dans `BackEnd/app.py`

## 📄 Licence

© 2024 Sougui - Produits Artisanaux
