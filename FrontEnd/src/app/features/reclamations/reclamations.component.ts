import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from '../../shared/components/navbar/navbar.component';
import { ReclamationService, Reclamation } from '../../core/services/reclamation.service';
import { TranslationService } from '../../core/services/translation.service';

@Component({
  selector: 'app-reclamations',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent],
  templateUrl: './reclamations.component.html',
  styleUrls: ['./reclamations.component.css']
})
export class ReclamationsComponent implements OnInit {
  reclamations = signal<Reclamation[]>([]);
  filteredReclamations = signal<Reclamation[]>([]);
  showModal = signal<boolean>(false);
  showDetailModal = signal<boolean>(false);
  selectedReclamation = signal<Reclamation | null>(null);
  isLoading = signal<boolean>(false);
  message = signal<string>('');

  searchTerm: string = '';
  filterStatus: string = '';
  filterPriority: string = '';

  reclamationForm = {
    title: '',
    description: '',
    category: 'technique' as 'technique' | 'commercial' | 'produit' | 'service' | 'autre',
    priority: 'moyenne' as 'basse' | 'moyenne' | 'haute' | 'urgente',
    attachment: null as string | null,
    attachment_name: '',
    attachment_type: ''
  };

  constructor(
    private reclamationService: ReclamationService,
    public translationService: TranslationService
  ) {}

  ngOnInit(): void {
    this.loadReclamations();
  }

  loadReclamations(): void {
    this.isLoading.set(true);
    this.reclamationService.getReclamations().subscribe({
      next: (response) => {
        this.reclamations.set(response.reclamations);
        this.filteredReclamations.set(response.reclamations);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false)
    });
  }

  filterReclamations(): void {
    let filtered = this.reclamations();

    // Filter by search term
    if (this.searchTerm) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(r => 
        r.title.toLowerCase().includes(term) ||
        r.description.toLowerCase().includes(term)
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

    this.filteredReclamations.set(filtered);
  }

  openModal(): void {
    this.showModal.set(true);
    this.resetForm();
  }

  closeModal(): void {
    this.showModal.set(false);
  }

  createReclamation(): void {
    // Validate title
    if (!this.reclamationForm.title || !this.reclamationForm.title.trim()) {
      this.message.set(this.translationService.translate('reclamations.error.titleRequired'));
      return;
    }

    if (this.reclamationForm.title.trim().length < 5) {
      this.message.set(this.translationService.translate('reclamations.error.titleTooShort'));
      return;
    }

    if (this.reclamationForm.title.trim().length > 200) {
      this.message.set(this.translationService.translate('reclamations.error.titleTooLong'));
      return;
    }

    // Validate description
    if (!this.reclamationForm.description || !this.reclamationForm.description.trim()) {
      this.message.set(this.translationService.translate('reclamations.error.descriptionRequired'));
      return;
    }

    if (this.reclamationForm.description.trim().length < 10) {
      this.message.set(this.translationService.translate('reclamations.error.descriptionTooShort'));
      return;
    }

    if (this.reclamationForm.description.trim().length > 2000) {
      this.message.set(this.translationService.translate('reclamations.error.descriptionTooLong'));
      return;
    }

    // Validate category
    if (!this.reclamationForm.category) {
      this.message.set(this.translationService.translate('reclamations.error.categoryRequired'));
      return;
    }

    // Validate priority
    if (!this.reclamationForm.priority) {
      this.message.set(this.translationService.translate('reclamations.error.priorityRequired'));
      return;
    }

    this.isLoading.set(true);
    this.message.set('');
    
    this.reclamationService.createReclamation(this.reclamationForm).subscribe({
      next: () => {
        this.isLoading.set(false);
        this.message.set(this.translationService.translate('reclamations.success'));
        this.closeModal();
        this.loadReclamations();
      },
      error: (error) => {
        this.isLoading.set(false);
        this.message.set(error.error?.message || this.translationService.translate('reclamations.error.createFailed'));
      }
    });
  }

  deleteReclamation(id: number): void {
    const confirmMsg = this.translationService.translate('reclamations.confirmDelete');
    if (confirm(confirmMsg)) {
      this.reclamationService.deleteReclamation(id).subscribe({
        next: () => this.loadReclamations()
      });
    }
  }

  resetForm(): void {
    this.reclamationForm = {
      title: '',
      description: '',
      category: 'technique',
      priority: 'moyenne',
      attachment: null,
      attachment_name: '',
      attachment_type: ''
    };
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      // Check file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        this.message.set(this.translationService.translate('reclamations.error.fileTooLarge'));
        return;
      }

      const reader = new FileReader();
      reader.onload = () => {
        this.reclamationForm.attachment = reader.result as string;
        this.reclamationForm.attachment_name = file.name;
        this.reclamationForm.attachment_type = file.type;
      };
      reader.readAsDataURL(file);
    }
  }

  removeAttachment(): void {
    this.reclamationForm.attachment = null;
    this.reclamationForm.attachment_name = '';
    this.reclamationForm.attachment_type = '';
  }

  viewDetails(reclamation: Reclamation): void {
    this.selectedReclamation.set(reclamation);
    this.showDetailModal.set(true);
  }

  closeDetailModal(): void {
    this.showDetailModal.set(false);
    this.selectedReclamation.set(null);
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
        this.message.set(this.translationService.translate('reclamations.error.downloadFailed'));
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
}
