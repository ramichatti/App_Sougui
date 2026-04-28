import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { ReclamationService, Reclamation } from '../../../core/services/reclamation.service';
import { TranslationService } from '../../../core/services/translation.service';
import { StatsCardComponent } from '../../../shared/components/stats-card/stats-card.component';
import { NotificationService } from '../../../core/services/notification.service';

@Component({
  selector: 'app-admin-reclamations',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent, StatsCardComponent],
  templateUrl: './admin-reclamations.component.html',
  styleUrls: ['./admin-reclamations.component.css']
})
export class AdminReclamationsComponent implements OnInit {
  reclamations = signal<Reclamation[]>([]);
  filteredReclamations = signal<Reclamation[]>([]);
  stats = signal<any>(null);
  showModal = signal<boolean>(false);
  selectedReclamation = signal<Reclamation | null>(null);
  isLoading = signal<boolean>(false);

  // Filters
  searchTerm = '';
  filterStatus: string = '';
  filterPriority: string = '';
  filterCategory: string = '';

  responseForm = {
    status: 'en_cours' as 'nouvelle' | 'en_cours' | 'resolue' | 'fermee',
    response: '',
    priority: 'moyenne' as 'basse' | 'moyenne' | 'haute' | 'urgente'
  };

  constructor(
    private reclamationService: ReclamationService,
    public translationService: TranslationService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadReclamations();
    this.loadStats();
    this.markAllAsNotified();
  }

  markAllAsNotified(): void {
    // Mark all new reclamations as notified when admin opens the page
    this.reclamationService.markNotified().subscribe();
  }

  loadReclamations(): void {
    this.isLoading.set(true);
    this.reclamationService.getReclamations().subscribe({
      next: (response) => {
        this.reclamations.set(response.reclamations);
        this.filteredReclamations.set(response.reclamations);
        this.isLoading.set(false);
      },
      error: () => {
        this.isLoading.set(false);
        this.notificationService.error('Erreur lors du chargement des réclamations');
      }
    });
  }

  loadStats(): void {
    this.reclamationService.getStats().subscribe({
      next: (stats) => this.stats.set(stats),
      error: () => this.notificationService.error('Erreur lors du chargement des statistiques')
    });
  }

  filterReclamations(): void {
    let filtered = this.reclamations();

    // Filter by search term
    if (this.searchTerm) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(r => 
        r.title.toLowerCase().includes(term) ||
        r.description.toLowerCase().includes(term) ||
        r.user_name.toLowerCase().includes(term) ||
        r.user_email.toLowerCase().includes(term)
      );
    }

    // Filter by status
    if (this.filterStatus) {
      filtered = filtered.filter(r => r.status === this.filterStatus);
    }

    // Filter by priority
    if (this.filterPriority) {
      filtered = filtered.filter(r => r.priority === this.filterPriority);
    }

    // Filter by category
    if (this.filterCategory) {
      filtered = filtered.filter(r => r.category === this.filterCategory);
    }

    this.filteredReclamations.set(filtered);
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.filterStatus = '';
    this.filterPriority = '';
    this.filterCategory = '';
    this.filteredReclamations.set(this.reclamations());
  }

  filterByStatus(status: string): void {
    this.filterStatus = status;
    this.filterReclamations();
  }

  openModal(reclamation: Reclamation): void {
    this.selectedReclamation.set(reclamation);
    this.responseForm = {
      status: reclamation.status,
      response: reclamation.response || '',
      priority: reclamation.priority
    };
    this.showModal.set(true);
  }

  closeModal(): void {
    this.showModal.set(false);
    this.selectedReclamation.set(null);
  }

  updateReclamation(): void {
    const reclamation = this.selectedReclamation();
    if (!reclamation) return;

    // Validation
    if (!this.responseForm.response || !this.responseForm.response.trim()) {
      this.notificationService.error('La réponse est requise');
      return;
    }

    if (this.responseForm.response.trim().length < 10) {
      this.notificationService.error('La réponse doit contenir au moins 10 caractères');
      return;
    }

    this.reclamationService.updateReclamation(reclamation.id, this.responseForm).subscribe({
      next: () => {
        this.loadReclamations();
        this.loadStats();
        this.closeModal();
        this.notificationService.success(
          this.translationService.translate('admin.reclamations.updateSuccess')
        );
      },
      error: () => {
        this.notificationService.error(
          this.translationService.translate('admin.reclamations.updateError')
        );
      }
    });
  }

  getStatusLabel(status: string): string {
    return this.translationService.translate(`status.${status}`);
  }

  getCategoryLabel(category: string): string {
    return this.translationService.translate(`category.${category}`);
  }

  getPriorityLabel(priority: string): string {
    return this.translationService.translate(`priority.${priority}`);
  }

  getStatusCount(status: string): number {
    return this.reclamations().filter(r => r.status === status).length;
  }

  getUserImage(reclamation: Reclamation): string {
    if (reclamation.user_image) {
      const base64Image = reclamation.user_image;
      // Check if it already has the data URI prefix
      if (base64Image.startsWith('data:image')) {
        return base64Image;
      }
      return 'data:image/jpeg;base64,' + base64Image;
    }
    // Generate avatar with user initials
    const names = reclamation.user_name.split(' ');
    const initials = names.map(n => n[0]).join('');
    return 'https://ui-avatars.com/api/?name=' + encodeURIComponent(reclamation.user_name) + '&size=80&background=1e3a8a&color=fff&bold=true';
  }

  downloadAttachment(reclamation: Reclamation): void {
    if (!reclamation.has_attachment) return;

    this.reclamationService.getAttachment(reclamation.id).subscribe({
      next: (response) => {
        const link = document.createElement('a');
        link.href = `data:${response.type};base64,${response.attachment}`;
        link.download = response.name;
        link.click();
      },
      error: () => {
        this.notificationService.error('Erreur lors du téléchargement de la pièce jointe');
      }
    });
  }

  deleteReclamation(id: number): void {
    const confirmMsg = this.translationService.translate('reclamations.confirmDelete');
    if (confirm(confirmMsg)) {
      this.reclamationService.deleteReclamation(id).subscribe({
        next: () => {
          this.loadReclamations();
          this.loadStats();
          this.notificationService.success('Réclamation supprimée avec succès');
        },
        error: () => {
          this.notificationService.error('Erreur lors de la suppression');
        }
      });
    }
  }
}
