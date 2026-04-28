# Sougui Frontend - Angular Application

Application décisionnelle pour l'entreprise Sougui avec thème bleu et blanc.

## Technologies
- Angular 17 (Standalone Components)
- TypeScript
- CSS3

## Fonctionnalités
- ✅ Authentification (Login)
- ✅ Mot de passe oublié avec code à expiration (15 minutes)
- ✅ 3 rôles: Admin, Directeur Vente, Directeur Achat
- ✅ Dashboards Power BI intégrés (iframe)
- ✅ Backoffice Admin (gestion utilisateurs et dashboards)
- ✅ Thème bleu et blanc

## Installation

### 1. Installer Node.js
Télécharger et installer Node.js depuis: https://nodejs.org/ (version LTS recommandée)

### 2. Installer Angular CLI
```bash
npm install -g @angular/cli
```

### 3. Installer les dépendances
```bash
npm install
```

### 4. Configuration
Le fichier `src/environments/environment.ts` contient l'URL de l'API backend:
```typescript
apiUrl: 'http://localhost:5000/api'
```

### 5. Lancer l'application
```bash
npm start
```
ou
```bash
ng serve
```

L'application sera disponible sur: http://localhost:4200

## Structure du Projet

```
src/
├── app/
│   ├── core/
│   │   ├── guards/          # Guards de navigation
│   │   ├── interceptors/    # HTTP Interceptors
│   │   ├── models/          # Interfaces TypeScript
│   │   └── services/        # Services Angular
│   ├── features/
│   │   ├── auth/            # Login et mot de passe oublié
│   │   ├── dashboard/       # Dashboards Power BI
│   │   └── admin/           # Backoffice admin
│   ├── app.component.ts
│   └── app.routes.ts
├── environments/            # Configuration environnement
├── styles.css              # Styles globaux (thème bleu/blanc)
└── index.html
```

## Comptes par défaut
Après initialisation du backend:
- **Admin**: admin@sougui.com / admin123
- **Directeur Vente**: vente@sougui.com / vente123
- **Directeur Achat**: achat@sougui.com / achat123

## Routes
- `/login` - Page de connexion
- `/forgot-password` - Réinitialisation mot de passe
- `/dashboard` - Dashboards utilisateur
- `/admin` - Backoffice admin (Admin uniquement)

## Thème
Couleurs principales:
- Bleu primaire: #1e3a8a
- Bleu secondaire: #3b82f6
- Blanc: #ffffff
- Gris clair: #f3f4f6

## Build Production
```bash
ng build --configuration production
```

Les fichiers seront générés dans `dist/sougui-frontend/`
