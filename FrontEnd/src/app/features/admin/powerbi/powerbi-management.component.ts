import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PowerBIService, PowerBIDashboard } from '../../../core/services/powerbi.service';
import { TranslationService } from '../../../core/services/translation.service';
import { NotificationService } from '../../../core/services/notification.service';

@Component({
  selector: 'app-powerbi-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './powerbi-management.component.html',
  styleUrls: ['./powerbi-management.component.css']
})
export class PowerBIManagementComponent implements OnInit {
  dashboards = signal<PowerBIDashboard[]>([]);
  showModal = signal<boolean>(false);
  editingDashboard = signal<PowerBIDashboard | null>(null);
  isLoading = signal<boolean>(false);
  selectedFilter = signal<string>('all');
  dashboardSearch = '';

  dashboardForm = {
    dashboard_name: '',
    embed_url: '',
    description: '',
    is_active: true
  };

  constructor(
    private powerbiService: PowerBIService,
    public translationService: TranslationService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadDashboards();
  }

  loadDashboards(): void {
    this.isLoading.set(true);
    this.powerbiService.getAllDashboards().subscribe({
      next: (response) => {
        this.dashboards.set(response.dashboards);
        this.isLoading.set(false);
      },
      error: () => {
        this.isLoading.set(false);
        this.notificationService.error('Failed to load dashboards');
      }
    });
  }

  openModal(dashboard?: PowerBIDashboard): void {
    if (dashboard) {
      this.editingDashboard.set(dashboard);
      this.dashboardForm = {
        dashboard_name: dashboard.dashboard_name,
        embed_url: dashboard.embed_url,
        description: dashboard.description || '',
        is_active: dashboard.is_active
      };
    } else {
      this.editingDashboard.set(null);
      this.resetForm();
    }
    this.showModal.set(true);
  }

  closeModal(): void {
    this.showModal.set(false);
    this.resetForm();
  }

  saveDashboard(): void {
    const dashboard = this.editingDashboard();
    
    if (dashboard) {
      this.powerbiService.updateDashboard(dashboard.id, this.dashboardForm).subscribe({
        next: () => {
          this.notificationService.success('Dashboard updated successfully');
          this.closeModal();
          this.loadDashboards();
        },
        error: () => {
          this.notificationService.error('Failed to update dashboard');
        }
      });
    } else {
      this.powerbiService.createDashboard(this.dashboardForm).subscribe({
        next: () => {
          this.notificationService.success('Dashboard created successfully');
          this.closeModal();
          this.loadDashboards();
        },
        error: () => {
          this.notificationService.error('Failed to create dashboard');
        }
      });
    }
  }

  copyUrl(url: string): void {
    navigator.clipboard.writeText(url).then(() => {
      this.notificationService.success('URL copiée dans le presse-papiers');
    }).catch(() => {
      this.notificationService.error('Impossible de copier l\'URL');
    });
  }

  deleteDashboard(id: number): void {
    if (confirm('Supprimer ce dashboard ? Cette action est irréversible.')) {
      this.powerbiService.deleteDashboard(id).subscribe({
        next: () => {
          this.notificationService.success('Dashboard deleted successfully');
          this.loadDashboards();
        },
        error: () => {
          this.notificationService.error('Failed to delete dashboard');
        }
      });
    }
  }

  resetForm(): void {
    this.dashboardForm = {
      dashboard_name: '',
      embed_url: '',
      description: '',
      is_active: true
    };
  }

  getFilteredDashboards(): PowerBIDashboard[] {
    let list = this.dashboards();
    const filter = this.selectedFilter();
    if (filter === 'active') list = list.filter(d => d.is_active);
    else if (filter === 'inactive') list = list.filter(d => !d.is_active);
    const q = this.dashboardSearch.toLowerCase().trim();
    if (q) list = list.filter(d =>
      d.dashboard_name.toLowerCase().includes(q) ||
      (d.description || '').toLowerCase().includes(q)
    );
    return list;
  }

  setFilter(filter: string): void {
    this.selectedFilter.set(filter);
  }

  get activeDashboardCount(): number {
    return this.dashboards().filter(d => d.is_active).length;
  }

  get inactiveDashboardCount(): number {
    return this.dashboards().filter(d => !d.is_active).length;
  }
}
