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
    
    // Forgot Password
    'forgot.title': { fr: '🔐 Mot de passe oublié', en: '🔐 Forgot Password' },
    'forgot.step1': { fr: 'Étape 1/3 : Entrez votre email pour recevoir un code de vérification', en: 'Step 1/3: Enter your email to receive a verification code' },
    'forgot.step2': { fr: 'Étape 2/3 : Entrez le code reçu par email', en: 'Step 2/3: Enter the code received by email' },
    'forgot.step3': { fr: 'Étape 3/3 : Créez votre nouveau mot de passe', en: 'Step 3/3: Create your new password' },
    'forgot.email.label': { fr: 'Adresse Email', en: 'Email Address' },
    'forgot.email.placeholder': { fr: 'exemple@sougui.com', en: 'example@sougui.com' },
    'forgot.email.hint': { fr: 'Entrez l\'email associé à votre compte', en: 'Enter the email associated with your account' },
    'forgot.email.submit': { fr: 'Envoyer le code', en: 'Send Code' },
    'forgot.email.sending': { fr: 'Envoi en cours...', en: 'Sending...' },
    'forgot.code.label': { fr: 'Code de vérification', en: 'Verification Code' },
    'forgot.code.placeholder': { fr: '000000', en: '000000' },
    'forgot.code.hint': { fr: 'Entrez le code à 6 chiffres reçu par email', en: 'Enter the 6-digit code received by email' },
    'forgot.code.submit': { fr: 'Vérifier le code', en: 'Verify Code' },
    'forgot.code.verifying': { fr: 'Vérification...', en: 'Verifying...' },
    'forgot.password.newLabel': { fr: 'Nouveau mot de passe', en: 'New Password' },
    'forgot.password.newPlaceholder': { fr: '••••••••', en: '••••••••' },
    'forgot.password.newHint': { fr: 'Minimum 6 caractères', en: 'Minimum 6 characters' },
    'forgot.password.confirmLabel': { fr: 'Confirmer le mot de passe', en: 'Confirm Password' },
    'forgot.password.confirmPlaceholder': { fr: '••••••••', en: '••••••••' },
    'forgot.password.confirmHint': { fr: 'Répétez le même mot de passe', en: 'Repeat the same password' },
    'forgot.password.submit': { fr: 'Réinitialiser le mot de passe', en: 'Reset Password' },
    'forgot.password.resetting': { fr: 'Réinitialisation...', en: 'Resetting...' },
    'forgot.backToLogin': { fr: 'Retour à la connexion', en: 'Back to Login' },
    'forgot.error.emailRequired': { fr: 'Veuillez entrer votre email', en: 'Please enter your email' },
    'forgot.error.emailInvalid': { fr: 'Format d\'email invalide', en: 'Invalid email format' },
    'forgot.error.codeRequired': { fr: 'Veuillez entrer le code', en: 'Please enter the code' },
    'forgot.error.codeLength': { fr: 'Le code doit contenir exactement 6 chiffres', en: 'Code must be exactly 6 digits' },
    'forgot.error.codeNumeric': { fr: 'Le code doit contenir uniquement des chiffres', en: 'Code must contain only digits' },
    'forgot.error.passwordRequired': { fr: 'Veuillez remplir tous les champs', en: 'Please fill all fields' },
    'forgot.error.passwordTooShort': { fr: 'Le mot de passe doit contenir au moins 6 caractères', en: 'Password must be at least 6 characters' },
    'forgot.error.passwordMismatch': { fr: 'Les mots de passe ne correspondent pas', en: 'Passwords do not match' },
    'forgot.error.sendCode': { fr: 'Erreur lors de l\'envoi du code', en: 'Error sending code' },
    'forgot.error.invalidCode': { fr: 'Code invalide ou expiré', en: 'Invalid or expired code' },
    'forgot.error.resetFailed': { fr: 'Erreur lors de la réinitialisation', en: 'Error during reset' },
    'forgot.error.emailFirst': { fr: 'Veuillez d\'abord demander un code par email', en: 'Please request a code by email first' },
    'forgot.error.verifyFirst': { fr: 'Veuillez d\'abord vérifier le code', en: 'Please verify the code first' },
    'forgot.success.codeSent': { fr: 'Code envoyé à {email}. Vérifiez votre boîte de réception (expire dans 15 minutes).', en: 'Code sent to {email}. Check your inbox (expires in 15 minutes).' },
    'forgot.success.codeVerified': { fr: '✅ Code vérifié ! Créez votre nouveau mot de passe', en: '✅ Code verified! Create your new password' },
    'forgot.success.passwordReset': { fr: '✅ Mot de passe réinitialisé avec succès ! Redirection...', en: '✅ Password reset successfully! Redirecting...' },
    
    // Toast notifications
    'toast.login.blocked.title': { fr: 'Compte Bloqué', en: 'Account Blocked' },
    'toast.login.blocked.message': { fr: 'Votre compte a été désactivé par l\'administrateur. Contactez le support.', en: 'Your account has been disabled by the administrator. Contact support.' },
    'toast.login.notFound.title': { fr: 'Email Introuvable', en: 'Email Not Found' },
    'toast.login.notFound.message': { fr: 'Aucun compte n\'est associé à cet email. Vérifiez l\'orthographe.', en: 'No account is associated with this email. Check the spelling.' },
    'toast.login.wrongPassword.title': { fr: 'Mot de Passe Incorrect', en: 'Incorrect Password' },
    'toast.login.wrongPassword.message': { fr: 'Le mot de passe saisi ne correspond pas. Réessayez ou réinitialisez-le.', en: 'The password entered does not match. Try again or reset it.' },
    'toast.login.error.title': { fr: 'Erreur de Connexion', en: 'Connection Error' },
    'toast.login.error.message': { fr: 'Une erreur est survenue. Veuillez réessayer.', en: 'An error occurred. Please try again.' },
    'toast.forgot.codeSent.title': { fr: 'Code Envoyé', en: 'Code Sent' },
    'toast.forgot.codeSent.message': { fr: 'Vérifiez votre boîte de réception (expire dans 15 minutes).', en: 'Check your inbox (expires in 15 minutes).' },
    'toast.forgot.codeVerified.title': { fr: 'Code Vérifié', en: 'Code Verified' },
    'toast.forgot.codeVerified.message': { fr: 'Créez maintenant votre nouveau mot de passe.', en: 'Now create your new password.' },
    'toast.forgot.passwordReset.title': { fr: 'Succès', en: 'Success' },
    'toast.forgot.passwordReset.message': { fr: 'Mot de passe réinitialisé ! Redirection vers la connexion...', en: 'Password reset! Redirecting to login...' },
    'toast.forgot.error.title': { fr: 'Erreur', en: 'Error' },
    
    // Home
    'home.welcome': { fr: 'Bienvenue sur Sougui', en: 'Welcome to Sougui' },
    'home.description': { fr: 'Votre plateforme décisionnelle pour la gestion des produits artisanaux', en: 'Your business intelligence platform for handcrafted products management' },
    'home.biPlatform': { fr: 'Plateforme BI & ML', en: 'BI & ML Platform' },
    
    // Hero Section
    'home.hero.badge': { fr: 'Plateforme Décisionnelle Ultime', en: 'Ultimate Decision Intelligence Platform' },
    'home.hero.title.main': { fr: 'Transformez vos Données en', en: 'Transform Data into' },
    'home.hero.title.highlight': { fr: 'Décisions Intelligentes', en: 'Intelligent Decisions' },
    'home.hero.title.sub': { fr: 'avec la Puissance du ML & BI', en: 'with ML & BI Power' },
    'home.hero.subtitle': { 
      fr: 'Exploitez la puissance du Machine Learning et de la Business Intelligence pour prendre des décisions basées sur les données pour votre entreprise de produits artisanaux', 
      en: 'Harness the power of Machine Learning and Business Intelligence to drive data-driven decisions for your handcrafted products business' 
    },
    'home.hero.subtitle.highlight': { fr: 'décisions basées sur les données', en: 'data-driven decisions' },
    
    // Hero Features
    'home.hero.feature1': { fr: 'Business Intelligence', en: 'Business Intelligence' },
    'home.hero.feature1.desc': { fr: 'Tableaux de bord en temps réel avec analyses interactives et suivi des KPI', en: 'Real-time dashboards with interactive analytics and KPI tracking' },
    'home.hero.feature1.badge': { fr: 'Temps Réel', en: 'Real-time' },
    'home.hero.feature2': { fr: 'Machine Learning', en: 'Machine Learning' },
    'home.hero.feature2.desc': { fr: 'Analyses prédictives et automatisation intelligente pour des opérations plus intelligentes', en: 'Predictive analytics and intelligent automation for smarter operations' },
    'home.hero.feature2.badge': { fr: 'Propulsé par l\'IA', en: 'AI-Powered' },
    'home.hero.feature3': { fr: 'Décisions Intelligentes', en: 'Smart Decisions' },
    'home.hero.feature3.desc': { fr: 'Insights basés sur les données et recommandations actionnables à portée de main', en: 'Data-driven insights and actionable recommendations at your fingertips' },
    'home.hero.feature3.badge': { fr: 'Actionnable', en: 'Actionable' },
    
    // Hero CTA
    'home.hero.cta.start': { fr: 'Commencer Votre Parcours', en: 'Start Your Journey' },
    'home.hero.cta.explore': { fr: 'Explorer les Fonctionnalités', en: 'Explore Features' },
    
    // Hero Trust Badges
    'home.hero.trust1': { fr: 'Sécurité de Niveau Entreprise', en: 'Enterprise-Grade Security' },
    'home.hero.trust2': { fr: 'Performance Ultra-Rapide', en: 'Lightning Fast Performance' },
    'home.hero.trust3': { fr: 'Support 24/7 Disponible', en: '24/7 Support Available' },
    
    // Stats
    'home.stats.support': { fr: 'Support', en: 'Support' },
    
    'home.yourTools': { fr: 'Vos Outils', en: 'Your Tools' },
    'home.quickActions': { fr: 'Actions Rapides', en: 'Quick Actions' },
    'home.bi.title': { fr: 'Business Intelligence', en: 'Business Intelligence' },
    'home.ml.title': { fr: 'Machine Learning', en: 'Machine Learning' },
    
    // Roles & Privileges (hardcoded text)
    'home.rolesPrivileges.title': { fr: 'Rôles & Privilèges', en: 'Roles & Privileges' },
    'home.rolesPrivileges.desc': { fr: 'Gérez les rôles utilisateurs et leurs privilèges d\'accès', en: 'Manage user roles and their access privileges' },
    'home.powerbi.desc': { fr: 'Configurez et gérez vos dashboards Power BI', en: 'Configure and manage your Power BI dashboards' },
    'home.dashboards.title': { fr: 'Configurer Dashboards', en: 'Configure Dashboards' },
    'home.dashboards.desc': { fr: 'Ajoutez et configurez de nouveaux dashboards Power BI', en: 'Add and configure new Power BI dashboards' },
    
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
      fr: 'Centralisez la gestion des utilisateurs et les notifications en temps réel',
      en: 'Centralize user management and real-time notifications'
    },
    'home.purpose.card3.point1': { fr: 'Gestion des rôles et accès', en: 'Role and access management' },
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
    'home.feature.dashboard.desc': { fr: 'Visualisez vos données avec des tableaux de bord interactifs', en: 'Visualize your data with interactive dashboards' },
    'home.feature.profile.desc': { fr: 'Gérez vos informations personnelles et paramètres', en: 'Manage your personal information and settings' },
    'home.feature.manage': { fr: 'Gérer', en: 'Manage' },
    'home.feature.view': { fr: 'Voir', en: 'View' },
    'home.feature.access': { fr: 'Accéder', en: 'Access' },
    'home.feature.consult': { fr: 'Consulter', en: 'Consult' },
    'home.action.newuser.desc': { fr: 'Créer un compte', en: 'Create an account' },
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
    
    // Roles
    'role.admin': { fr: 'Administrateur', en: 'Administrator' },
    'role.directeur_vente': { fr: 'Directeur Vente', en: 'Sales Director' },
    'role.directeur_achat': { fr: 'Directeur Achat', en: 'Purchase Director' },
    
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
    
    // Dashboard
    'dashboard.title': { fr: 'Mes Dashboards', en: 'My Dashboards' },
    'dashboard.subtitle': { fr: 'Visualisez vos tableaux de bord Power BI', en: 'View your Power BI dashboards' },
    'dashboard.admin': { fr: 'Administration', en: 'Administration' },
    'dashboard.logout': { fr: 'Déconnexion', en: 'Logout' },
    'dashboard.loading': { fr: 'Chargement des dashboards...', en: 'Loading dashboards...' },
    'dashboard.refresh': { fr: 'Actualiser', en: 'Refresh' },
    'dashboard.retry': { fr: 'Réessayer', en: 'Retry' },
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
    'notification.noNotificationsDesc': { fr: 'Vous êtes à jour !', en: 'You\'re all caught up!' },
    'notification.markAllRead': { fr: 'Tout marquer comme lu', en: 'Mark all as read' },
    'notification.justNow': { fr: 'À l\'instant', en: 'Just now' },
    'notification.minutesAgo': { fr: 'min', en: 'min ago' },
    'notification.hoursAgo': { fr: 'h', en: 'h ago' },
    'notification.daysAgo': { fr: 'j', en: 'd ago' },
    'notification.privilegeGranted': { fr: 'Nouveau privilège accordé', en: 'New privilege granted' },
    
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
