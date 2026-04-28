import { Injectable, signal } from '@angular/core';

export type Language = 'fr' | 'en';

interface Translations {
  [key: string]: {
    fr: string;
    en: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class TranslationService {
  currentLanguage = signal<Language>('fr');

  private translations: Translations = {
    // Navigation
    'nav.home': { fr: 'Accueil', en: 'Home' },
    'nav.users': { fr: 'Utilisateurs', en: 'Users' },
    'nav.reclamations': { fr: 'Réclamations', en: 'Claims' },
    'nav.powerbi': { fr: 'Dashboards BI', en: 'BI Dashboards' },
    'nav.dashboard': { fr: 'Dashboards', en: 'Dashboards' },
    'nav.profile': { fr: 'Profil', en: 'Profile' },
    'nav.logout': { fr: 'Déconnexion', en: 'Logout' },
    'nav.language': { fr: 'Langue', en: 'Language' },
    
    // Login
    'login.title': { fr: 'Sougui', en: 'Sougui' },
    'login.subtitle': { fr: 'Application Décisionnelle', en: 'Business Intelligence App' },
    'login.email': { fr: 'Email', en: 'Email' },
    'login.password': { fr: 'Mot de passe', en: 'Password' },
    'login.forgotPassword': { fr: 'Mot de passe oublié ?', en: 'Forgot password?' },
    'login.submit': { fr: 'Se connecter', en: 'Sign in' },
    'login.loading': { fr: 'Connexion en cours...', en: 'Signing in...' },
    'login.footer': { fr: '© 2024 Sougui - Produits Artisanaux', en: '© 2024 Sougui - Handcrafted Products' },
    'login.error.fillFields': { fr: 'Veuillez remplir tous les champs', en: 'Please fill all fields' },
    'login.error.connection': { fr: 'Erreur de connexion', en: 'Connection error' },
    'login.error.emailRequired': { fr: 'L\'email est requis', en: 'Email is required' },
    'login.error.emailInvalid': { fr: 'Format d\'email invalide', en: 'Invalid email format' },
    'login.error.passwordRequired': { fr: 'Le mot de passe est requis', en: 'Password is required' },
    'login.error.passwordTooShort': { fr: 'Le mot de passe doit contenir au moins 6 caractères', en: 'Password must be at least 6 characters' },
    
    // Home
    'home.welcome': { fr: 'Bienvenue sur Sougui', en: 'Welcome to Sougui' },
    'home.description': { fr: 'Votre plateforme décisionnelle pour la gestion des produits artisanaux', en: 'Your business intelligence platform for handcrafted products management' },
    'home.biPlatform': { fr: 'Plateforme BI & ML', en: 'BI & ML Platform' },
    'home.hero.feature1': { fr: 'Business Intelligence', en: 'Business Intelligence' },
    'home.hero.feature1.desc': { fr: 'Tableaux de bord interactifs et analyses en temps réel', en: 'Interactive dashboards and real-time analytics' },
    'home.hero.feature2': { fr: 'Machine Learning', en: 'Machine Learning' },
    'home.hero.feature2.desc': { fr: 'Prédictions intelligentes et optimisation automatique', en: 'Smart predictions and automatic optimization' },
    'home.hero.feature3': { fr: 'Décisions Éclairées', en: 'Informed Decisions' },
    'home.hero.feature3.desc': { fr: 'Insights actionnables basés sur vos données', en: 'Actionable insights based on your data' },
    'home.hero.cta.start': { fr: 'Commencer Maintenant', en: 'Get Started Now' },
    'home.hero.cta.learn': { fr: 'En Savoir Plus', en: 'Learn More' },
    'home.yourTools': { fr: 'Vos Outils', en: 'Your Tools' },
    'home.quickActions': { fr: 'Actions Rapides', en: 'Quick Actions' },
    'home.bi.title': { fr: 'Business Intelligence', en: 'Business Intelligence' },
    'home.ml.title': { fr: 'Machine Learning', en: 'Machine Learning' },
    
    // Application Purpose
    'home.purpose.badge': { fr: 'Notre Mission', en: 'Our Mission' },
    'home.purpose.title': { fr: 'Une Plateforme Décisionnelle Complète pour Sougui', en: 'A Complete Decision-Making Platform for Sougui' },
    'home.purpose.description': { 
      fr: 'Sougui BI Platform transforme vos données en insights actionnables grâce à l\'intelligence artificielle et l\'analyse avancée. Notre solution aide les dirigeants à prendre des décisions éclairées basées sur des données en temps réel.', 
      en: 'Sougui BI Platform transforms your data into actionable insights through artificial intelligence and advanced analytics. Our solution helps leaders make informed decisions based on real-time data.' 
    },
    
    // Purpose Cards
    'home.purpose.card1.title': { fr: 'Analyse en Temps Réel', en: 'Real-Time Analysis' },
    'home.purpose.card1.description': { 
      fr: 'Visualisez vos données instantanément avec des tableaux de bord interactifs Power BI', 
      en: 'Visualize your data instantly with interactive Power BI dashboards' 
    },
    'home.purpose.card1.point1': { fr: 'Dashboards personnalisés par rôle', en: 'Role-customized dashboards' },
    'home.purpose.card1.point2': { fr: 'Métriques KPI en direct', en: 'Live KPI metrics' },
    'home.purpose.card1.point3': { fr: 'Rapports automatisés', en: 'Automated reports' },
    
    'home.purpose.card2.title': { fr: 'Intelligence Artificielle', en: 'Artificial Intelligence' },
    'home.purpose.card2.description': { 
      fr: 'Anticipez les tendances et optimisez vos opérations avec le Machine Learning', 
      en: 'Anticipate trends and optimize your operations with Machine Learning' 
    },
    'home.purpose.card2.point1': { fr: 'Prédictions de ventes', en: 'Sales predictions' },
    'home.purpose.card2.point2': { fr: 'Optimisation des stocks', en: 'Inventory optimization' },
    'home.purpose.card2.point3': { fr: 'Détection d\'anomalies', en: 'Anomaly detection' },
    
    'home.purpose.card3.title': { fr: 'Gestion Collaborative', en: 'Collaborative Management' },
    'home.purpose.card3.description': { 
      fr: 'Centralisez la communication et le suivi des réclamations en un seul endroit', 
      en: 'Centralize communication and claims tracking in one place' 
    },
    'home.purpose.card3.point1': { fr: 'Suivi des réclamations', en: 'Claims tracking' },
    'home.purpose.card3.point2': { fr: 'Gestion des utilisateurs', en: 'User management' },
    'home.purpose.card3.point3': { fr: 'Notifications en temps réel', en: 'Real-time notifications' },
    
    // Key Benefits
    'home.benefits.title': { fr: 'Pourquoi Choisir Sougui BI Platform ?', en: 'Why Choose Sougui BI Platform?' },
    'home.benefits.benefit1.title': { fr: 'Décisions Basées sur les Données', en: 'Data-Driven Decisions' },
    'home.benefits.benefit1.description': { 
      fr: 'Prenez des décisions stratégiques éclairées grâce à des analyses approfondies et des visualisations claires de vos données d\'entreprise.', 
      en: 'Make informed strategic decisions through in-depth analysis and clear visualizations of your business data.' 
    },
    'home.benefits.benefit2.title': { fr: 'Gain de Temps Considérable', en: 'Significant Time Savings' },
    'home.benefits.benefit2.description': { 
      fr: 'Automatisez vos rapports et analyses pour vous concentrer sur ce qui compte vraiment : la croissance de votre entreprise.', 
      en: 'Automate your reports and analyses to focus on what really matters: growing your business.' 
    },
    'home.benefits.benefit3.title': { fr: 'Prédictions Précises', en: 'Accurate Predictions' },
    'home.benefits.benefit3.description': { 
      fr: 'Anticipez les tendances du marché et les besoins futurs grâce à nos algorithmes de Machine Learning avancés.', 
      en: 'Anticipate market trends and future needs with our advanced Machine Learning algorithms.' 
    },
    'home.benefits.benefit4.title': { fr: 'Collaboration Améliorée', en: 'Enhanced Collaboration' },
    'home.benefits.benefit4.description': { 
      fr: 'Facilitez la communication entre les départements avec des outils de gestion centralisés et des notifications instantanées.', 
      en: 'Facilitate communication between departments with centralized management tools and instant notifications.' 
    },
    'home.feature.users.desc': { fr: 'Créez, modifiez et gérez tous les utilisateurs de la plateforme', en: 'Create, edit and manage all platform users' },
    'home.feature.reclamations.desc': { fr: 'Suivez et traitez toutes les réclamations des utilisateurs', en: 'Track and process all user claims' },
    'home.feature.dashboard.desc': { fr: 'Visualisez vos données avec des tableaux de bord interactifs', en: 'Visualize your data with interactive dashboards' },
    'home.feature.myreclamations.desc': { fr: 'Créez et suivez l\'état de vos réclamations', en: 'Create and track your claims status' },
    'home.feature.profile.desc': { fr: 'Gérez vos informations personnelles et paramètres', en: 'Manage your personal information and settings' },
    'home.feature.manage': { fr: 'Gérer', en: 'Manage' },
    'home.feature.view': { fr: 'Voir', en: 'View' },
    'home.feature.access': { fr: 'Accéder', en: 'Access' },
    'home.feature.consult': { fr: 'Consulter', en: 'Consult' },
    'home.action.newuser.desc': { fr: 'Créer un compte', en: 'Create an account' },
    'home.action.newclaim.desc': { fr: 'Soumettre une réclamation', en: 'Submit a claim' },
    'home.action.stats': { fr: 'Voir Statistiques', en: 'View Statistics' },
    'home.action.stats.desc': { fr: 'Consulter les données', en: 'View data' },
    'home.action.security.desc': { fr: 'Sécurité du compte', en: 'Account security' },
    
    // Profile
    'profile.title': { fr: 'Mon Profil', en: 'My Profile' },
    'profile.description': { fr: 'Gérez vos informations personnelles et votre sécurité', en: 'Manage your personal information and security' },
    'profile.photo': { fr: 'Photo de Profil', en: 'Profile Photo' },
    'profile.changePhoto': { fr: 'Changer la photo', en: 'Change photo' },
    'profile.updatePhoto': { fr: 'Mettre à jour la photo', en: 'Update photo' },
    'profile.uploading': { fr: 'Téléchargement...', en: 'Uploading...' },
    'profile.personalInfo': { fr: 'Informations Personnelles', en: 'Personal Information' },
    'profile.firstName': { fr: 'Prénom', en: 'First Name' },
    'profile.lastName': { fr: 'Nom', en: 'Last Name' },
    'profile.email': { fr: 'Email', en: 'Email' },
    'profile.update': { fr: 'Mettre à jour', en: 'Update' },
    'profile.updating': { fr: 'Mise à jour...', en: 'Updating...' },
    'profile.changePassword': { fr: 'Changer le Mot de Passe', en: 'Change Password' },
    'profile.currentPassword': { fr: 'Mot de passe actuel', en: 'Current password' },
    'profile.newPassword': { fr: 'Nouveau mot de passe', en: 'New password' },
    'profile.confirmPassword': { fr: 'Confirmer le mot de passe', en: 'Confirm password' },
    'profile.changePasswordBtn': { fr: 'Changer le mot de passe', en: 'Change password' },
    'profile.changing': { fr: 'Changement...', en: 'Changing...' },
    'profile.invalidImageType': { fr: 'Veuillez sélectionner un fichier image valide', en: 'Please select a valid image file' },
    'profile.imageTooLarge': { fr: 'La taille de l\'image doit être inférieure à 5MB', en: 'Image size must be less than 5MB' },
    'profile.passwordHint': { fr: 'Au moins 6 caractères avec majuscule, minuscule et chiffre', en: 'At least 6 characters with uppercase, lowercase and number' },
    
    // Reclamations
    'reclamations.title': { fr: 'Mes Réclamations', en: 'My Claims' },
    'reclamations.new': { fr: 'Nouvelle Réclamation', en: 'New Claim' },
    'reclamations.noReclamations': { fr: 'Aucune réclamation', en: 'No claims' },
    'reclamations.noReclamationsDesc': { fr: 'Vous n\'avez pas encore créé de réclamation', en: 'You haven\'t created any claims yet' },
    'reclamations.title_field': { fr: 'Titre', en: 'Title' },
    'reclamations.category': { fr: 'Catégorie', en: 'Category' },
    'reclamations.priority': { fr: 'Priorité', en: 'Priority' },
    'reclamations.description': { fr: 'Description', en: 'Description' },
    'reclamations.response': { fr: 'Réponse', en: 'Response' },
    'reclamations.create': { fr: 'Créer', en: 'Create' },
    'reclamations.creating': { fr: 'Création...', en: 'Creating...' },
    'reclamations.cancel': { fr: 'Annuler', en: 'Cancel' },
    'reclamations.createdOn': { fr: 'Créée le', en: 'Created on' },
    'reclamations.success': { fr: 'Réclamation créée avec succès', en: 'Claim created successfully' },
    'reclamations.confirmDelete': { fr: 'Êtes-vous sûr de vouloir supprimer cette réclamation ?', en: 'Are you sure you want to delete this claim?' },
    'reclamations.titlePlaceholder': { fr: 'Ex: Problème avec la commande #1234', en: 'Ex: Issue with order #1234' },
    'reclamations.titleHint': { fr: 'Entre 5 et 200 caractères', en: 'Between 5 and 200 characters' },
    'reclamations.descriptionPlaceholder': { fr: 'Décrivez votre réclamation en détail...', en: 'Describe your claim in detail...' },
    'reclamations.descriptionHint': { fr: 'Entre 10 et 2000 caractères', en: 'Between 10 and 2000 characters' },
    'reclamations.error.titleRequired': { fr: 'Le titre est requis', en: 'Title is required' },
    'reclamations.error.titleTooShort': { fr: 'Le titre doit contenir au moins 5 caractères', en: 'Title must be at least 5 characters' },
    'reclamations.error.titleTooLong': { fr: 'Le titre ne peut pas dépasser 200 caractères', en: 'Title cannot exceed 200 characters' },
    'reclamations.error.descriptionRequired': { fr: 'La description est requise', en: 'Description is required' },
    'reclamations.error.descriptionTooShort': { fr: 'La description doit contenir au moins 10 caractères', en: 'Description must be at least 10 characters' },
    'reclamations.error.descriptionTooLong': { fr: 'La description ne peut pas dépasser 2000 caractères', en: 'Description cannot exceed 2000 characters' },
    'reclamations.error.categoryRequired': { fr: 'La catégorie est requise', en: 'Category is required' },
    'reclamations.error.priorityRequired': { fr: 'La priorité est requise', en: 'Priority is required' },
    'reclamations.error.createFailed': { fr: 'Erreur lors de la création de la réclamation', en: 'Error creating claim' },
    
    // Admin
    'admin.users.title': { fr: 'Gestion des Utilisateurs', en: 'User Management' },
    'admin.users.subtitle': { fr: 'Gérez les comptes et les permissions des utilisateurs', en: 'Manage user accounts and permissions' },
    'admin.users.new': { fr: 'Nouvel Utilisateur', en: 'New User' },
    'admin.users.name': { fr: 'Nom', en: 'Name' },
    'admin.users.email': { fr: 'Email', en: 'Email' },
    'admin.users.role': { fr: 'Rôle', en: 'Role' },
    'admin.users.status': { fr: 'Statut', en: 'Status' },
    'admin.users.actions': { fr: 'Actions', en: 'Actions' },
    'admin.users.edit': { fr: 'Modifier', en: 'Edit' },
    'admin.users.delete': { fr: 'Supprimer', en: 'Delete' },
    'admin.users.active': { fr: 'Actif', en: 'Active' },
    'admin.users.inactive': { fr: 'Inactif', en: 'Inactive' },
    'admin.users.editUser': { fr: 'Modifier l\'utilisateur', en: 'Edit user' },
    'admin.users.newUser': { fr: 'Nouvel utilisateur', en: 'New user' },
    'admin.users.firstName': { fr: 'Prénom', en: 'First Name' },
    'admin.users.lastName': { fr: 'Nom', en: 'Last Name' },
    'admin.users.password': { fr: 'Mot de passe', en: 'Password' },
    'admin.users.passwordHint': { fr: '(laisser vide pour ne pas changer)', en: '(leave blank to keep unchanged)' },
    'admin.users.accountActive': { fr: 'Compte actif', en: 'Active account' },
    'admin.users.confirmDelete': { fr: 'Êtes-vous sûr de vouloir supprimer cet utilisateur ?', en: 'Are you sure you want to delete this user?' },
    'admin.users.search': { fr: 'Rechercher par nom ou email...', en: 'Search by name or email...' },
    'admin.users.filter.all': { fr: 'Tous', en: 'All' },
    'admin.users.stats.total': { fr: 'Total Utilisateurs', en: 'Total Users' },
    'admin.users.stats.active': { fr: 'Utilisateurs Actifs', en: 'Active Users' },
    'admin.users.stats.admins': { fr: 'Administrateurs', en: 'Administrators' },
    'admin.users.stats.directors': { fr: 'Directeurs', en: 'Directors' },
    'admin.users.noUsers': { fr: 'Aucun utilisateur trouvé', en: 'No users found' },
    'admin.users.noUsersDesc': { fr: 'Essayez de modifier vos critères de recherche', en: 'Try adjusting your search criteria' },
    'admin.users.gridView': { fr: 'Vue en grille', en: 'Grid view' },
    'admin.users.listView': { fr: 'Vue en liste', en: 'List view' },
    'admin.users.user': { fr: 'Utilisateur', en: 'User' },
    'admin.users.firstNameHint': { fr: 'Entre 2 et 50 caractères', en: 'Between 2 and 50 characters' },
    'admin.users.lastNameHint': { fr: 'Entre 2 et 50 caractères', en: 'Between 2 and 50 characters' },
    'admin.users.emailHint': { fr: 'Format: exemple@domaine.com', en: 'Format: example@domain.com' },
    'admin.users.passwordStrengthHint': { fr: 'Minimum 6 caractères', en: 'Minimum 6 characters' },
    'admin.users.roleHint': { fr: 'Sélectionnez le rôle approprié', en: 'Select the appropriate role' },
    
    'admin.reclamations.title': { fr: 'Gestion des Réclamations', en: 'Claims Management' },
    'admin.reclamations.subtitle': { fr: 'Gérez et traitez toutes les réclamations des utilisateurs', en: 'Manage and process all user claims' },
    'admin.reclamations.total': { fr: 'Total', en: 'Total' },
    'admin.reclamations.new': { fr: 'Nouvelles', en: 'New' },
    'admin.reclamations.inProgress': { fr: 'En cours', en: 'In Progress' },
    'admin.reclamations.resolved': { fr: 'Résolues', en: 'Resolved' },
    'admin.reclamations.closed': { fr: 'Fermées', en: 'Closed' },
    'admin.reclamations.treat': { fr: 'Traiter', en: 'Process' },
    'admin.reclamations.treatTitle': { fr: 'Traiter la Réclamation', en: 'Process Claim' },
    'admin.reclamations.by': { fr: 'Par', en: 'By' },
    'admin.reclamations.responsePlaceholder': { fr: 'Votre réponse à la réclamation...', en: 'Your response to the claim...' },
    'admin.reclamations.noReclamations': { fr: 'Aucune réclamation', en: 'No claims' },
    'admin.reclamations.noReclamationsDesc': { fr: 'Aucune réclamation ne correspond à vos critères de recherche', en: 'No claims match your search criteria' },
    
    // Roles
    'role.admin': { fr: 'Administrateur', en: 'Administrator' },
    'role.directeur_vente': { fr: 'Directeur Vente', en: 'Sales Director' },
    'role.directeur_achat': { fr: 'Directeur Achat', en: 'Purchase Director' },
    
    // Status
    'status.nouvelle': { fr: 'Nouvelle', en: 'New' },
    'status.en_cours': { fr: 'En cours', en: 'In Progress' },
    'status.resolue': { fr: 'Résolue', en: 'Resolved' },
    'status.fermee': { fr: 'Fermée', en: 'Closed' },
    
    // Categories
    'category.technique': { fr: 'Technique', en: 'Technical' },
    'category.commercial': { fr: 'Commercial', en: 'Commercial' },
    'category.produit': { fr: 'Produit', en: 'Product' },
    'category.service': { fr: 'Service', en: 'Service' },
    'category.autre': { fr: 'Autre', en: 'Other' },
    
    // Priority
    'priority.basse': { fr: 'Basse', en: 'Low' },
    'priority.moyenne': { fr: 'Moyenne', en: 'Medium' },
    'priority.haute': { fr: 'Haute', en: 'High' },
    'priority.urgente': { fr: 'Urgente', en: 'Urgent' },
    
    // Common
    'common.loading': { fr: 'Chargement...', en: 'Loading...' },
    'common.save': { fr: 'Enregistrer', en: 'Save' },
    'common.cancel': { fr: 'Annuler', en: 'Cancel' },
    'common.delete': { fr: 'Supprimer', en: 'Delete' },
    'common.edit': { fr: 'Modifier', en: 'Edit' },
    'common.close': { fr: 'Fermer', en: 'Close' },
    'common.search': { fr: 'Rechercher...', en: 'Search...' },
    'common.filter': { fr: 'Filtrer', en: 'Filter' },
    'common.export': { fr: 'Exporter', en: 'Export' },
    'common.exportSuccess': { fr: 'Export réussi', en: 'Export successful' },
    'common.active': { fr: 'Actif', en: 'Active' },
    
    // Admin reclamations messages
    'admin.reclamations.updateSuccess': { fr: 'Réclamation mise à jour avec succès', en: 'Claim updated successfully' },
    'admin.reclamations.updateError': { fr: 'Erreur lors de la mise à jour', en: 'Error updating claim' },
    
    // Reclamations filters
    'reclamations.allStatus': { fr: 'Tous les statuts', en: 'All statuses' },
    'reclamations.allPriority': { fr: 'Toutes les priorités', en: 'All priorities' },
    
    // Dashboard
    'dashboard.noDashboards': { fr: 'Aucun dashboard disponible', en: 'No dashboards available' },
    'dashboard.noDashboardsDesc': { fr: 'Contactez l\'administrateur pour configurer vos dashboards Power BI', en: 'Contact the administrator to configure your Power BI dashboards' },
    'dashboard.error': { fr: 'Erreur lors du chargement des dashboards', en: 'Error loading dashboards' },
    
    // Role-specific BI/ML descriptions - Admin
    'home.role.admin.title': { 
      fr: 'Tableau de Bord Administrateur', 
      en: 'Administrator Dashboard' 
    },
    'home.role.admin.description': { 
      fr: 'Supervisez l\'ensemble de l\'organisation avec des outils BI et ML avancés pour une gestion optimale', 
      en: 'Oversee the entire organization with advanced BI and ML tools for optimal management' 
    },
    'home.role.admin.bi.description': { 
      fr: 'Visualisez les performances globales de l\'entreprise avec des tableaux de bord interactifs et des rapports détaillés', 
      en: 'Visualize overall company performance with interactive dashboards and detailed reports' 
    },
    'home.role.admin.bi.feature1': { 
      fr: 'Tableaux de bord consolidés multi-départements', 
      en: 'Consolidated multi-department dashboards' 
    },
    'home.role.admin.bi.feature2': { 
      fr: 'Analyse des KPIs en temps réel', 
      en: 'Real-time KPI analysis' 
    },
    'home.role.admin.bi.feature3': { 
      fr: 'Rapports de performance comparatifs', 
      en: 'Comparative performance reports' 
    },
    'home.role.admin.bi.feature4': { 
      fr: 'Visualisation des tendances historiques', 
      en: 'Historical trend visualization' 
    },
    'home.role.admin.ml.description': { 
      fr: 'Utilisez l\'intelligence artificielle pour prédire les tendances et optimiser les décisions stratégiques', 
      en: 'Use artificial intelligence to predict trends and optimize strategic decisions' 
    },
    'home.role.admin.ml.feature1': { 
      fr: 'Prédiction des ventes futures', 
      en: 'Future sales prediction' 
    },
    'home.role.admin.ml.feature2': { 
      fr: 'Détection d\'anomalies dans les opérations', 
      en: 'Anomaly detection in operations' 
    },
    'home.role.admin.ml.feature3': { 
      fr: 'Recommandations stratégiques automatisées', 
      en: 'Automated strategic recommendations' 
    },
    'home.role.admin.ml.feature4': { 
      fr: 'Analyse prédictive des risques', 
      en: 'Predictive risk analysis' 
    },
    
    // Role-specific BI/ML descriptions - Directeur Vente
    'home.role.directeur_vente.title': { 
      fr: 'Tableau de Bord Directeur Vente', 
      en: 'Sales Director Dashboard' 
    },
    'home.role.directeur_vente.description': { 
      fr: 'Optimisez vos stratégies commerciales avec des insights BI et des prédictions ML sur les ventes', 
      en: 'Optimize your sales strategies with BI insights and ML predictions on sales' 
    },
    'home.role.directeur_vente.bi.description': { 
      fr: 'Analysez les performances commerciales et identifiez les opportunités de croissance avec des données en temps réel', 
      en: 'Analyze sales performance and identify growth opportunities with real-time data' 
    },
    'home.role.directeur_vente.bi.feature1': { 
      fr: 'Suivi des ventes par produit et région', 
      en: 'Sales tracking by product and region' 
    },
    'home.role.directeur_vente.bi.feature2': { 
      fr: 'Analyse du pipeline commercial', 
      en: 'Sales pipeline analysis' 
    },
    'home.role.directeur_vente.bi.feature3': { 
      fr: 'Performance des équipes de vente', 
      en: 'Sales team performance' 
    },
    'home.role.directeur_vente.bi.feature4': { 
      fr: 'Taux de conversion et ROI', 
      en: 'Conversion rates and ROI' 
    },
    'home.role.directeur_vente.ml.description': { 
      fr: 'Anticipez les tendances du marché et optimisez vos prévisions de ventes grâce au Machine Learning', 
      en: 'Anticipate market trends and optimize your sales forecasts with Machine Learning' 
    },
    'home.role.directeur_vente.ml.feature1': { 
      fr: 'Prévisions de demande par produit', 
      en: 'Product demand forecasting' 
    },
    'home.role.directeur_vente.ml.feature2': { 
      fr: 'Segmentation intelligente des clients', 
      en: 'Intelligent customer segmentation' 
    },
    'home.role.directeur_vente.ml.feature3': { 
      fr: 'Recommandations de prix optimaux', 
      en: 'Optimal pricing recommendations' 
    },
    'home.role.directeur_vente.ml.feature4': { 
      fr: 'Prédiction du churn client', 
      en: 'Customer churn prediction' 
    },
    
    // Role-specific BI/ML descriptions - Directeur Achat
    'home.role.directeur_achat.title': { 
      fr: 'Tableau de Bord Directeur Achat', 
      en: 'Purchase Director Dashboard' 
    },
    'home.role.directeur_achat.description': { 
      fr: 'Gérez efficacement vos approvisionnements avec des analyses BI et des prédictions ML sur les stocks', 
      en: 'Efficiently manage your supplies with BI analytics and ML predictions on inventory' 
    },
    'home.role.directeur_achat.bi.description': { 
      fr: 'Optimisez votre chaîne d\'approvisionnement avec des analyses détaillées des coûts et des fournisseurs', 
      en: 'Optimize your supply chain with detailed cost and supplier analysis' 
    },
    'home.role.directeur_achat.bi.feature1': { 
      fr: 'Analyse des coûts d\'approvisionnement', 
      en: 'Procurement cost analysis' 
    },
    'home.role.directeur_achat.bi.feature2': { 
      fr: 'Performance des fournisseurs', 
      en: 'Supplier performance' 
    },
    'home.role.directeur_achat.bi.feature3': { 
      fr: 'Suivi des niveaux de stock', 
      en: 'Inventory level tracking' 
    },
    'home.role.directeur_achat.bi.feature4': { 
      fr: 'Analyse des délais de livraison', 
      en: 'Delivery time analysis' 
    },
    'home.role.directeur_achat.ml.description': { 
      fr: 'Prédisez les besoins en stock et optimisez vos commandes avec des algorithmes de Machine Learning', 
      en: 'Predict inventory needs and optimize your orders with Machine Learning algorithms' 
    },
    'home.role.directeur_achat.ml.feature1': { 
      fr: 'Prévision des besoins en stock', 
      en: 'Inventory needs forecasting' 
    },
    'home.role.directeur_achat.ml.feature2': { 
      fr: 'Optimisation des quantités de commande', 
      en: 'Order quantity optimization' 
    },
    'home.role.directeur_achat.ml.feature3': { 
      fr: 'Détection des ruptures de stock', 
      en: 'Stock-out detection' 
    },
    'home.role.directeur_achat.ml.feature4': { 
      fr: 'Prédiction des variations de prix', 
      en: 'Price variation prediction' 
    },

    // Footer
    'footer.tagline': { fr: 'Produits Artisanaux Tunisiens de Qualité', en: 'Quality Tunisian Handcrafted Products' },
    'footer.company': { fr: 'Entreprise', en: 'Company' },
    'footer.about': { fr: 'À Propos', en: 'About Us' },
    'footer.products': { fr: 'Nos Produits', en: 'Our Products' },
    'footer.artisans': { fr: 'Nos Artisans', en: 'Our Artisans' },
    'footer.contact': { fr: 'Contact', en: 'Contact' },
    'footer.platform': { fr: 'Plateforme', en: 'Platform' },
    'footer.resources': { fr: 'Ressources', en: 'Resources' },
    'footer.blog': { fr: 'Blog', en: 'Blog' },
    'footer.help': { fr: 'Aide', en: 'Help' },
    'footer.faq': { fr: 'FAQ', en: 'FAQ' },
    'footer.support': { fr: 'Support', en: 'Support' },
    'footer.visit': { fr: 'Visitez Notre Site', en: 'Visit Our Website' },
    'footer.visitDesc': { 
      fr: 'Découvrez notre collection complète de produits artisanaux tunisiens authentiques', 
      en: 'Discover our complete collection of authentic Tunisian handcrafted products' 
    },
    'footer.rights': { fr: 'Tous droits réservés', en: 'All rights reserved' },
    'footer.privacy': { fr: 'Confidentialité', en: 'Privacy Policy' },
    'footer.terms': { fr: 'Conditions', en: 'Terms of Service' },
    'footer.cookies': { fr: 'Cookies', en: 'Cookies' },
    'footer.madeWith': { fr: 'Fait avec', en: 'Made with' },
    'footer.inTunisia': { fr: 'en Tunisie', en: 'in Tunisia' },
    
    // Footer Newsletter
    'footer.newsletter.title': { fr: 'Restez Informé', en: 'Stay Informed' },
    'footer.newsletter.desc': { fr: 'Abonnez-vous à notre newsletter pour recevoir les dernières actualités', en: 'Subscribe to our newsletter to receive the latest news' },
    'footer.newsletter.placeholder': { fr: 'Votre adresse email', en: 'Your email address' },
    'footer.newsletter.button': { fr: 'S\'abonner', en: 'Subscribe' },
    
    // Footer Stats
    'footer.stats.products': { fr: 'Produits', en: 'Products' },
    'footer.stats.artisans': { fr: 'Artisans', en: 'Artisans' },
    'footer.stats.clients': { fr: 'Clients', en: 'Clients' },
    'footer.followUs': { fr: 'Suivez-nous', en: 'Follow Us' },
    
    // Notifications
    'notification.title': { fr: 'Notifications', en: 'Notifications' },
    'notification.noNotifications': { fr: 'Aucune notification', en: 'No notifications' },
    'notification.noNotificationsDesc': { fr: 'Vous êtes à jour!', en: 'You\'re all caught up!' },
    'notification.newClaim': { fr: 'Nouvelle réclamation', en: 'New claim' },
    'notification.viewAll': { fr: 'Voir toutes les réclamations', en: 'View all claims' },
    'notification.justNow': { fr: 'À l\'instant', en: 'Just now' },
    'notification.minutesAgo': { fr: 'min', en: 'min ago' },
    'notification.hoursAgo': { fr: 'h', en: 'h ago' },
    'notification.daysAgo': { fr: 'j', en: 'd ago' },
    'notification.unprocessedClaims': { fr: 'réclamations non traitées', en: 'unprocessed claims' },
    
    // Power BI Management
    'powerbi.title': { fr: 'Gestion des Dashboards Power BI', en: 'Power BI Dashboards Management' },
    'powerbi.subtitle': { fr: 'Gérez les dashboards Power BI pour chaque rôle', en: 'Manage Power BI dashboards for each role' },
    'powerbi.new': { fr: 'Nouveau Dashboard', en: 'New Dashboard' },
    'powerbi.total': { fr: 'Total Dashboards', en: 'Total Dashboards' },
    'powerbi.active': { fr: 'Actif', en: 'Active' },
    'powerbi.inactive': { fr: 'Inactif', en: 'Inactive' },
    'powerbi.role': { fr: 'Rôle', en: 'Role' },
    'powerbi.dashboardName': { fr: 'Nom du Dashboard', en: 'Dashboard Name' },
    'powerbi.embedUrl': { fr: 'URL d\'intégration', en: 'Embed URL' },
    'powerbi.embedUrlHint': { fr: 'Copiez l\'URL d\'intégration depuis Power BI', en: 'Copy the embed URL from Power BI' },
    'powerbi.description': { fr: 'Description', en: 'Description' },
    'powerbi.descriptionPlaceholder': { fr: 'Description du dashboard...', en: 'Dashboard description...' },
    'powerbi.dashboardActive': { fr: 'Dashboard actif', en: 'Active dashboard' },
    'powerbi.editDashboard': { fr: 'Modifier le Dashboard', en: 'Edit Dashboard' },
    'powerbi.newDashboard': { fr: 'Nouveau Dashboard', en: 'New Dashboard' },
    'powerbi.create': { fr: 'Créer', en: 'Create' },
    'powerbi.confirmDelete': { fr: 'Êtes-vous sûr de vouloir supprimer ce dashboard ?', en: 'Are you sure you want to delete this dashboard?' },
    'powerbi.noDashboards': { fr: 'Aucun dashboard', en: 'No dashboards' },
    'powerbi.noDashboardsDesc': { fr: 'Créez votre premier dashboard Power BI', en: 'Create your first Power BI dashboard' },
  };

  constructor() {
    // Load saved language
    const saved = localStorage.getItem('language') as Language;
    if (saved) {
      this.currentLanguage.set(saved);
    }
  }

  translate(key: string): string {
    const translation = this.translations[key];
    if (!translation) {
      return key;
    }
    return translation[this.currentLanguage()];
  }

  setLanguage(lang: Language): void {
    this.currentLanguage.set(lang);
    localStorage.setItem('language', lang);
  }

  toggleLanguage(): void {
    const newLang: Language = this.currentLanguage() === 'fr' ? 'en' : 'fr';
    this.setLanguage(newLang);
  }
}
