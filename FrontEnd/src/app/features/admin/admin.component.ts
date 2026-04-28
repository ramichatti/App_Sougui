import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { AdminService } from '../../core/services/admin.service';
import { DashboardService } from '../../core/services/dashboard.service';
import { User } from '../../core/models/user.model';
import { Dashboard } from '../../core/models/dashboard.model';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.css']
})
export class AdminComponent implements OnInit {
  activeTab = signal<'users' | 'dashboards'>('users');
  users = signal<User[]>([]);
  dashboards = signal<Dashboard[]>([]);
  isLoading = signal<boolean>(false);
  
  showUserModal = signal<boolean>(false);
  showDashboardModal = signal<boolean>(false);
  editingUser = signal<User | null>(null);
  editingDashboard = signal<Dashboard | null>(null);
  
  userForm = {
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'directeur_vente' as 'admin' | 'directeur_vente' | 'directeur_achat',
    is_active: true
  };
  
  dashboardForm = {
    role: 'directeur_vente' as 'admin' | 'directeur_vente' | 'directeur_achat',
    dashboard_name: '',
    embed_url: '',
    description: '',
    is_active: true
  };

  constructor(
    public authService: AuthService,
    private adminService: AdminService,
    private dashboardService: DashboardService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadUsers();
    this.loadDashboards();
  }

  loadUsers(): void {
    this.isLoading.set(true);
    this.adminService.getUsers().subscribe({
      next: (response) => {
        this.users.set(response.users);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false)
    });
  }

  loadDashboards(): void {
    this.isLoading.set(true);
    this.dashboardService.getAllDashboards().subscribe({
      next: (response) => {
        this.dashboards.set(response.dashboards);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false)
    });
  }

  openUserModal(user?: User): void {
    if (user) {
      this.editingUser.set(user);
      this.userForm = {
        email: user.email,
        password: '',
        first_name: user.first_name,
        last_name: user.last_name,
        role: user.role,
        is_active: user.is_active
      };
    } else {
      this.editingUser.set(null);
      this.resetUserForm();
    }
    this.showUserModal.set(true);
  }

  openDashboardModal(dashboard?: Dashboard): void {
    if (dashboard) {
      this.editingDashboard.set(dashboard);
      this.dashboardForm = {
        role: dashboard.role as any,
        dashboard_name: dashboard.dashboard_name,
        embed_url: dashboard.embed_url,
        description: dashboard.description || '',
        is_active: dashboard.is_active
      };
    } else {
      this.editingDashboard.set(null);
      this.resetDashboardForm();
    }
    this.showDashboardModal.set(true);
  }

  saveUser(): void {
    const user = this.editingUser();
    if (user) {
      this.adminService.updateUser(user.id, this.userForm).subscribe({
        next: () => {
          this.loadUsers();
          this.closeUserModal();
        }
      });
    } else {
      this.adminService.createUser(this.userForm).subscribe({
        next: () => {
          this.loadUsers();
          this.closeUserModal();
        }
      });
    }
  }

  deleteUser(id: number): void {
    if (confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ?')) {
      this.adminService.deleteUser(id).subscribe({
        next: () => this.loadUsers()
      });
    }
  }

  saveDashboard(): void {
    const dashboard = this.editingDashboard();
    if (dashboard) {
      this.dashboardService.updateDashboard(dashboard.id, this.dashboardForm).subscribe({
        next: () => {
          this.loadDashboards();
          this.closeDashboardModal();
        }
      });
    } else {
      this.dashboardService.createDashboard(this.dashboardForm).subscribe({
        next: () => {
          this.loadDashboards();
          this.closeDashboardModal();
        }
      });
    }
  }

  deleteDashboard(id: number): void {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce dashboard ?')) {
      this.dashboardService.deleteDashboard(id).subscribe({
        next: () => this.loadDashboards()
      });
    }
  }

  closeUserModal(): void {
    this.showUserModal.set(false);
    this.resetUserForm();
  }

  closeDashboardModal(): void {
    this.showDashboardModal.set(false);
    this.resetDashboardForm();
  }

  resetUserForm(): void {
    this.userForm = {
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      role: 'directeur_vente',
      is_active: true
    };
  }

  resetDashboardForm(): void {
    this.dashboardForm = {
      role: 'directeur_vente',
      dashboard_name: '',
      embed_url: '',
      description: '',
      is_active: true
    };
  }

  getRoleLabel(role: string): string {
    const labels: { [key: string]: string } = {
      'admin': 'Admin',
      'directeur_vente': 'Dir. Vente',
      'directeur_achat': 'Dir. Achat'
    };
    return labels[role] || role;
  }

  goToDashboard(): void {
    this.router.navigate(['/dashboard']);
  }

  logout(): void {
    this.authService.logout();
  }
}
