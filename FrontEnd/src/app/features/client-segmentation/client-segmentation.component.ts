import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TranslationService } from '../../core/services/translation.service';

interface Client {
  client_id: number;
  client_name: string;
  cluster: number;
  segment_name: string;
  ca_total: number;
  nb_commandes: number;
  panier_moyen: number;
  recency: number;
}

interface SegmentStats {
  segment_name: string;
  client_count: number;
}

@Component({
  selector: 'app-client-segmentation',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './client-segmentation.component.html',
  styleUrls: ['./client-segmentation.component.css']
})
export class ClientSegmentationComponent implements OnInit {
  clients: Client[] = [];
  filteredClients: Client[] = [];
  segmentStats: SegmentStats[] = [];
  loading = false;
  error: string | null = null;
  searchTerm = '';
  selectedSegment = 'all';
  
  // Pagination
  currentPage = 1;
  itemsPerPage = 10;
  totalPages = 1;
  
  // Statistiques
  totalClients = 0;
  
  // Couleurs des segments (adaptées aux vrais clusters du modèle)
  segmentColors: { [key: string]: string } = {
    '🌟 VIP Récents (Cluster 0)': '#10b981',
    '⚠️ Clients Perdus/Inactifs (Cluster 1)': '#ef4444',
    // Fallback pour les anciens noms
    'Champions': '#10b981',
    'Clients Fidèles': '#3b82f6',
    'Clients Potentiels': '#f59e0b',
    'Clients à Risque': '#ef4444',
    'Clients Perdus': '#6b7280'
  };

  // Méthodes pour la nouvelle UI
  selectSegment(segmentName: string): void {
    this.selectedSegment = segmentName;
    this.filterClients();
  }

  clearSearch(): void {
    this.searchTerm = '';
    this.filterClients();
  }

  getVipClientsCount(): number {
    const vipStat = this.segmentStats.find(s => s.segment_name.includes('VIP') || s.segment_name.includes('Champions'));
    return vipStat ? vipStat.client_count : 0;
  }

  getSegmentShortName(segmentName: string): string {
    if (segmentName.includes('VIP')) return 'VIP';
    if (segmentName.includes('Perdus') || segmentName.includes('Inactifs')) return 'Inactif';
    if (segmentName.includes('Champions')) return 'Champion';
    if (segmentName.includes('Fidèles')) return 'Fidèle';
    if (segmentName.includes('Potentiels')) return 'Potentiel';
    if (segmentName.includes('Risque')) return 'Risque';
    return segmentName.substring(0, 8);
  }

  constructor(private http: HttpClient, public translate: TranslationService) {}

  ngOnInit(): void {
    this.loadSegmentation();
  }

  loadSegmentation(): void {
    this.loading = true;
    this.error = null;

    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });

    this.http.post<any>(
      `${environment.apiUrl}/ml/balkis/client-segmentation`,
      {},
      { headers }
    ).subscribe({
      next: (response) => {
        this.clients = response.clients || [];
        this.filteredClients = [...this.clients];
        this.segmentStats = response.segment_stats || [];
        this.totalClients = response.total_clients || 0;
        this.updatePagination();
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement de la segmentation:', err);
        this.error = err.error?.error || 'Erreur lors du chargement de la segmentation';
        this.loading = false;
      }
    });
  }

  filterClients(): void {
    let filtered = [...this.clients];

    // Filtre par segment
    if (this.selectedSegment !== 'all') {
      filtered = filtered.filter(c => c.segment_name === this.selectedSegment);
    }

    // Filtre par recherche
    if (this.searchTerm.trim()) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(c =>
        c.client_name.toLowerCase().includes(term) ||
        c.client_id.toString().includes(term)
      );
    }

    this.filteredClients = filtered;
    this.currentPage = 1;
    this.updatePagination();
  }

  updatePagination(): void {
    this.totalPages = Math.ceil(this.filteredClients.length / this.itemsPerPage);
  }

  get paginatedClients(): Client[] {
    const start = (this.currentPage - 1) * this.itemsPerPage;
    const end = start + this.itemsPerPage;
    return this.filteredClients.slice(start, end);
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
    }
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
    }
  }

  goToPage(page: number): void {
    this.currentPage = page;
  }

  get pageNumbers(): number[] {
    const pages: number[] = [];
    const maxVisible = 5;
    let start = Math.max(1, this.currentPage - Math.floor(maxVisible / 2));
    let end = Math.min(this.totalPages, start + maxVisible - 1);

    if (end - start < maxVisible - 1) {
      start = Math.max(1, end - maxVisible + 1);
    }

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    return pages;
  }

  getSegmentColor(segmentName: string): string {
    return this.segmentColors[segmentName] || '#6b7280';
  }

  getSegmentPercentage(segmentName: string): number {
    const stat = this.segmentStats.find(s => s.segment_name === segmentName);
    if (!stat || this.totalClients === 0) return 0;
    return (stat.client_count / this.totalClients) * 100;
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('fr-TN', {
      style: 'currency',
      currency: 'TND',
      minimumFractionDigits: 2
    }).format(value);
  }

  exportToCSV(): void {
    const headers = ['ID Client', 'Nom', 'Segment', 'CA Total', 'Nb Commandes', 'Panier Moyen', 'Récence (jours)'];
    const rows = this.filteredClients.map(c => [
      c.client_id,
      c.client_name,
      c.segment_name,
      c.ca_total,
      c.nb_commandes,
      c.panier_moyen,
      c.recency
    ]);

    let csv = headers.join(',') + '\n';
    rows.forEach(row => {
      csv += row.join(',') + '\n';
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `segmentation-clients-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  }
}
