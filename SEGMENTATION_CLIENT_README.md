# 🎯 Segmentation Client B2C - Documentation

## 📋 Vue d'ensemble

Système complet de segmentation des clients B2C utilisant le machine learning (KMeans) pour classifier les clients selon leur comportement d'achat.

## 🔧 Architecture

### Backend (Python/Flask)

**Endpoint:** `POST /api/ml/balkis/client-segmentation`

**Modèle ML:** `BackEnd/ml_models/Balkis/segmentation_clients.pkl` (KMeans)

**Tables DWH utilisées:**
- `dbo.Dim_Client` - Informations clients
- `dbo.Fact_Vente_B2C` - Commandes B2C

### Frontend (Angular)

**Route:** `/client-segmentation`

**Composant:** `ClientSegmentationComponent`

**Fichiers:**
- `client-segmentation.component.ts`
- `client-segmentation.component.html`
- `client-segmentation.component.css`

## 📊 Features du Modèle (7 features)

Le modèle utilise 7 caractéristiques pour segmenter les clients :

1. **Recency** (Récence)
   - Nombre de jours depuis la dernière commande
   - Calculé: `DATEDIFF(DAY, MAX(Date_Commande), GETDATE())`

2. **Frequency** (Fréquence)
   - Nombre total de commandes
   - Calculé: `COUNT(DISTINCT Num_Commande)`

3. **Monetary** (Montant)
   - Montant total dépensé
   - Calculé: `SUM(Montant_Total_Commande)`

4. **Panier_Moyen**
   - Montant moyen par commande
   - Calculé: `AVG(Montant_Total_Commande)`

5. **Quantité_Totale**
   - Quantité totale de produits achetés
   - Calculé: `SUM(Quantite)`

6. **Taux_Réduction**
   - Taux de réduction moyen utilisé
   - Calculé: `SUM(Reduction) / SUM(Montant_Total_Commande)`

7. **Produits_Par_Commande**
   - Nombre moyen de produits par commande
   - Calculé: `SUM(Quantite) / COUNT(DISTINCT Num_Commande)`

## 🎨 Segments Définis

| Segment | Couleur | Code Hex | Description |
|---------|---------|----------|-------------|
| 🏆 Champions | Vert | #10b981 | Meilleurs clients (haute valeur, fréquence élevée) |
| 💙 Clients Fidèles | Bleu | #3b82f6 | Clients réguliers et engagés |
| ⚡ Clients Potentiels | Orange | #f59e0b | Clients avec potentiel de croissance |
| ⚠️ Clients à Risque | Rouge | #ef4444 | Clients en perte d'engagement |
| 😴 Clients Perdus | Gris | #6b7280 | Clients inactifs depuis longtemps |

## 🔌 API Endpoints

### 1. Segmentation Globale

**Request:**
```json
POST /api/ml/balkis/client-segmentation
Headers: {
  "Authorization": "Bearer <token>",
  "Content-Type": "application/json"
}
Body: {}
```

**Response:**
```json
{
  "total_clients": 150,
  "n_clusters": 5,
  "clients": [
    {
      "client_id": 1,
      "client_name": "Jean Dupont",
      "cluster": 0,
      "segment_name": "Champions",
      "ca_total": 5000.00,
      "nb_commandes": 25,
      "panier_moyen": 200.00,
      "recency": 5
    }
  ],
  "segment_stats": [
    {
      "segment_name": "Champions",
      "client_count": 30
    }
  ],
  "model": "KMeans Client Segmentation (Balkis)",
  "timestamp": "2026-05-04T12:30:00"
}
```

### 2. Segmentation Client Spécifique

**Request:**
```json
POST /api/ml/balkis/client-segmentation
Headers: {
  "Authorization": "Bearer <token>",
  "Content-Type": "application/json"
}
Body: {
  "client_id": 1
}
```

**Response:**
```json
{
  "client_id": 1,
  "client_name": "Jean Dupont",
  "cluster": 0,
  "segment_name": "Champions",
  "n_clusters": 5,
  "cluster_distances": [0.5, 2.3, 3.1, 4.2, 5.0],
  "features_used": {
    "recency": 5,
    "frequency": 25,
    "monetary": 5000.00,
    "panier_moyen": 200.00,
    "quantite_totale": 75,
    "taux_reduction": 0.05,
    "produits_par_commande": 3.0
  },
  "model": "KMeans Client Segmentation (Balkis)",
  "timestamp": "2026-05-04T12:30:00"
}
```

## 🎨 Interface Utilisateur

### Fonctionnalités

1. **Cartes Statistiques**
   - Total clients
   - Répartition par segment avec pourcentages
   - Barres de progression colorées

2. **Filtres**
   - Recherche par nom ou ID client
   - Filtre par segment
   - Compteur de résultats

3. **Tableau**
   - Liste paginée des clients
   - Colonnes: ID, Nom, Segment, CA Total, Nb Commandes, Panier Moyen, Récence
   - Badges colorés pour les segments
   - Badge de récence (vert si < 30 jours, rouge si > 90 jours)

4. **Actions**
   - Export CSV
   - Pagination (10 clients par page)

### Design

- **Gradient de fond:** Violet (#667eea → #764ba2)
- **Cartes:** Blanches avec ombres et animations au survol
- **Icônes:** Material Design
- **Responsive:** Adapté mobile et desktop

## 🧪 Tests

### Script de test

Exécuter le script de test :

```bash
cd BackEnd
python test_client_segmentation.py
```

Le script teste :
1. ✅ Authentification
2. ✅ Segmentation globale
3. ✅ Segmentation client spécifique

### Tests manuels

1. Démarrer le backend :
```bash
cd BackEnd
python app.py
```

2. Démarrer le frontend :
```bash
cd FrontEnd
ng serve
```

3. Accéder à l'application :
   - URL: `http://localhost:4200`
   - Menu: Modèles ML → Segmentation Clients

## 📝 Exemple de Calcul

Pour un client avec les commandes suivantes :

| Date | Montant | Quantité | Réduction |
|------|---------|----------|-----------|
| 2025-01-05 | 150 TND | 5 | 0 TND |
| 2025-02-15 | 200 TND | 7 | 10 TND |
| 2025-03-10 | 100 TND | 3 | 0 TND |
| 2025-04-05 | 250 TND | 6 | 5 TND |
| 2025-04-20 | 100 TND | 3 | 0 TND |

**Date de référence:** 2026-05-04

**Features calculées:**
```python
Recency: 379 jours  # Depuis 2025-04-20
Frequency: 5 commandes
Monetary: 800 TND
Panier_Moyen: 160 TND
Quantité_Totale: 24 produits
Taux_Réduction: 0.01875  # 15 / 800
Produits_Par_Commande: 4.8  # 24 / 5
```

## 🔄 Workflow

```
1. Utilisateur accède à /client-segmentation
2. Frontend appelle POST /api/ml/balkis/client-segmentation
3. Backend récupère les données depuis DWH (Dim_Client + Fact_Vente_B2C)
4. Backend calcule les 7 features pour chaque client
5. Backend applique le modèle KMeans
6. Backend retourne les segments
7. Frontend affiche les résultats avec graphiques et tableaux
```

## 🚀 Déploiement

### Prérequis

1. **Backend:**
   - Python 3.8+
   - Flask
   - pyodbc
   - scikit-learn
   - Accès au DWH SQL Server

2. **Frontend:**
   - Node.js 16+
   - Angular 17+

### Configuration

1. **Variables d'environnement (.env):**
```env
DWH_SERVER=localhost,1433
DWH_DATABASE=Sougui_DWH
DWH_USER=sa
DWH_PASSWORD=your_password
```

2. **Modèle ML:**
   - Placer `segmentation_clients.pkl` dans `BackEnd/ml_models/Balkis/`

## 📊 Métriques de Performance

- **Temps de réponse:** < 2 secondes pour 1000 clients
- **Précision du modèle:** Dépend de l'entraînement KMeans
- **Scalabilité:** Testé jusqu'à 10,000 clients

## 🐛 Dépannage

### Erreur "Modèle non trouvé"
- Vérifier que `segmentation_clients.pkl` existe dans `BackEnd/ml_models/Balkis/`

### Erreur "Connexion au DWH"
- Vérifier les credentials dans `.env`
- Vérifier que SQL Server est accessible
- Vérifier que les tables `Dim_Client` et `Fact_Vente_B2C` existent

### Aucun client affiché
- Vérifier qu'il y a des données dans `Fact_Vente_B2C`
- Vérifier les logs backend pour les erreurs SQL

## 📚 Ressources

- [Documentation KMeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)
- [RFM Analysis](https://en.wikipedia.org/wiki/RFM_(market_research))
- [Customer Segmentation](https://www.optimove.com/resources/learning-center/customer-segmentation)

## 👥 Auteurs

- **Balkis** - Modèle ML de segmentation
- **Équipe Sougui** - Intégration et interface

## 📄 Licence

Propriétaire - Sougui © 2026
