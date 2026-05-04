import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { adminSecurityGuard } from './core/guards/admin-security.guard';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'forgot-password',
    loadComponent: () => import('./features/auth/forgot-password/forgot-password.component').then(m => m.ForgotPasswordComponent)
  },
  {
    path: 'home',
    loadComponent: () => import('./features/home/home.component').then(m => m.HomeComponent),
    canActivate: [authGuard]
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [authGuard]
  },
  {
    path: 'dashboard/:id',
    loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [authGuard]
  },
  {
    path: 'profile',
    loadComponent: () => import('./features/profile/profile.component').then(m => m.ProfileComponent),
    canActivate: [authGuard]
  },
  {
    path: 'admin/confirm',
    loadComponent: () => import('./features/admin/confirm/admin-confirm.component').then(m => m.AdminConfirmComponent),
    canActivate: [authGuard]
  },
  {
    path: 'admin/users',
    loadComponent: () => import('./features/admin/users/users.component').then(m => m.UsersComponent),
    canActivate: [authGuard, adminSecurityGuard]  // ✅ Double auth - Gestion utilisateurs
  },
  {
    path: 'admin/roles',
    loadComponent: () => import('./features/admin/roles/roles-management.component').then(m => m.RolesManagementComponent),
    canActivate: [authGuard, adminSecurityGuard]  // ✅ Double auth - Gestion rôles & accès
  },
  {
    path: 'admin/powerbi',
    loadComponent: () => import('./features/admin/powerbi/powerbi-management.component').then(m => m.PowerBIManagementComponent),
    canActivate: [authGuard, adminSecurityGuard]  // ✅ Double auth - Gestion dashboards (config admin)
  },
  {
    path: 'admin/email-settings',
    loadComponent: () => import('./features/admin/email-settings/email-settings.component').then(m => m.EmailSettingsComponent),
    canActivate: [authGuard, adminSecurityGuard]  // ✅ Double auth - Configuration email (sensible)
  },
  {
    path: 'admin/ml-models',
    loadComponent: () => import('./features/admin/ml-models/ml-models.component').then(m => m.MlModelsComponent),
    canActivate: [authGuard]  // ✅ Pas de double auth - Configuration modèles ML (utilisation)
  },
  // ============================================
  // MODÈLES ML
  // ============================================
  {
    path: 'predict-cost',
    loadComponent: () => import('./features/predict-cost/predict-cost.component').then(m => m.PredictCostComponent),
    canActivate: [authGuard]
  },
  {
    path: 'distance-analysis',
    loadComponent: () => import('./features/distance-analysis/distance-analysis.component').then(m => m.DistanceAnalysisComponent),
    canActivate: [authGuard]
  },
  {
    path: 'demand-prediction',
    loadComponent: () => import('./features/demand-prediction/demand-prediction.component').then(m => m.DemandPredictionComponent),
    canActivate: [authGuard]
  },
  {
    path: 'price-simulator',
    loadComponent: () => import('./features/price-simulator/price-simulator.component').then(m => m.PriceSimulatorComponent),
    canActivate: [authGuard]
  },
  {
    path: 'best-seller-b2c',
    loadComponent: () => import('./features/best-seller-b2c/best-seller-b2c.component').then(m => m.BestSellerB2cComponent),
    canActivate: [authGuard]
  },
  {
    path: 'client-segmentation',
    loadComponent: () => import('./features/client-segmentation/client-segmentation.component').then(m => m.ClientSegmentationComponent),
    canActivate: [authGuard]
  },
  {
    path: 'supplier-classification',
    loadComponent: () => import('./features/supplier-classification/supplier-classification.component').then(m => m.SupplierClassificationComponent),
    canActivate: [authGuard]
  },
  {
    path: '',
    redirectTo: '/login',
    pathMatch: 'full'
  },
  {
    path: '**',
    redirectTo: '/login'
  }
];