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
    canActivate: [authGuard, adminSecurityGuard]
  },
  {
    path: 'admin/roles',
    loadComponent: () => import('./features/admin/roles/roles-management.component').then(m => m.RolesManagementComponent),
    canActivate: [authGuard, adminSecurityGuard]
  },
  {
    path: 'admin/powerbi',
    loadComponent: () => import('./features/admin/powerbi/powerbi-management.component').then(m => m.PowerBIManagementComponent),
    canActivate: [authGuard, adminSecurityGuard]
  },
  {
    path: 'admin/models',
    loadComponent: () => import('./features/admin/models/models.component').then(m => m.ModelsComponent),
    canActivate: [authGuard, adminSecurityGuard]
  },
  {
    path: 'admin/models/best-seller',
    loadComponent: () => import('./features/admin/models/best-seller/best-seller.component').then(m => m.BestSellerComponent),
    canActivate: [authGuard, adminSecurityGuard]
  },
  {
    path: 'admin/models/kmeans',
    loadComponent: () => import('./features/admin/models/kmeans/kmeans.component').then(m => m.KmeansComponent),
    canActivate: [authGuard, adminSecurityGuard]
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
