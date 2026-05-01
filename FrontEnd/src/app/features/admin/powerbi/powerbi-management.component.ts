import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { DashboardService } from '../../../core/services/dashboard.service';
import { Dashboard } from '../../../core/models/dashboard.model';

interface DashboardForm {
  dashboard_name: string;
  embed_url: string;
  description: string;
  is_active: boolean;
}

@Component({
  selector: 'app-powerbi-management',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent],
  templateUrl: './powerbi-management.component.html',
  styleUrls: ['./powerbi-management.component.css']
})
export class PowerBIManagementComponent implements OnInit {
  dashboards = signal<Dashboard[]>([]);
  isLoading = signal<boolean>(true);
  showModal = signal<boolean>(false);
  editingDashboard = signal<Dashboard | null>(null);
  selectedFilter = signal<'all' | 'active' | 'inactive'>('all');
  dashboardSearch = '';

  dashboardForm: DashboardForm = {
    dashboard_name: '',
    embed_url: '',
    description: '',
    is_active: true
  };

  activeDashboardCount = computed(() => 
    this.dashboards().filter(d => d.is_active).length
  );

  inactiveDashboardCount = computed(() => 
    this.dashboards().filter(d => !d.is_active).length
  );

  constructor(private dashboardService: DashboardService) {}

  ngOnInit(): void {
    this.loadDashboards();
  }

  loadDashboards(): void {
    this.isLoading.set(true);
    this.dashboardService.getAllDashboards().subscribe({
      next: (response) => {
        this.dashboards.set(response.dashboards || []);
        this.isLoading.set(false);
      },
      error: (error) => {
        console.error('Error loading dashboards:', error);
        this.isLoading.set(false);
      }
    });
  }

  getFilteredDashboards(): Dashboard[] {
    let filtered = this.dashboards();

    if (this.selectedFilter() === 'active') {
      filtered = filtered.filter(d => d.is_active);
    } else if (this.selectedFilter() === 'inactive') {
      filtered = filtered.filter(d => !d.is_active);
    }

    if (this.dashboardSearch.trim()) {
      const search = this.dashboardSearch.toLowerCase();
      filtered = filtered.filter(d => 
        d.dashboard_name.toLowerCase().includes(search) ||
        (d.description && d.description.toLowerCase().includes(search)) ||
        d.embed_url.toLowerCase().includes(search)
      );
    }

    return filtered;
  }

  setFilter(filter: 'all' | 'active' | 'inactive'): void {
    this.selectedFilter.set(filter);
  }

  openModal(dashboard?: Dashboard): void {
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
      this.dashboardForm = {
        dashboard_name: '',
        embed_url: '',
        description: '',
        is_active: true
      };
    }
    this.showModal.set(true);
  }

  closeModal(): void {
    this.showModal.set(false);
    this.editingDashboard.set(null);
    this.dashboardForm = {
      dashboard_name: '',
      embed_url: '',
      description: '',
      is_active: true
    };
  }

  saveDashboard(): void {
    const editing = this.editingDashboard();
    
    if (editing) {
      this.dashboardService.updateDashboard(editing.id, this.dashboardForm).subscribe({
        next: () => {
          this.loadDashboards();
          this.closeModal();
        },
        error: (error) => {
          console.error('Error updating dashboard:', error);
          alert('Erreur lors de la mise à jour du dashboard');
        }
      });
    } else {
      this.dashboardService.createDashboard(this.dashboardForm).subscribe({
        next: () => {
          this.loadDashboards();
          this.closeModal();
        },
        error: (error) => {
          console.error('Error creating dashboard:', error);
          alert('Erreur lors de la création du dashboard');
        }
      });
    }
  }

  deleteDashboard(id: number): void {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce dashboard ?')) {
      this.dashboardService.deleteDashboard(id).subscribe({
        next: () => {
          this.loadDashboards();
        },
        error: (error) => {
          console.error('Error deleting dashboard:', error);
          alert('Erreur lors de la suppression du dashboard');
        }
      });
    }
  }

  copyUrl(url: string): void {
    navigator.clipboard.writeText(url).then(() => {
      console.log('URL copied to clipboard');
    }).catch(err => {
      console.error('Failed to copy URL:', err);
    });
  }
}
