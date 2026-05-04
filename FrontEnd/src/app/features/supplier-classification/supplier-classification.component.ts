import { Component, OnInit, signal, OnDestroy } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from '../../core/services/auth.service';
import { TranslationService } from '../../core/services/translation.service';
import { NotificationService } from '../../core/services/notification.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';

interface Supplier {
  id: number;
  nom: string;
  matricule_fiscal: string;
  telephone: string;
  nb_factures: number;
  nb_produits: number;
  montant_total_ht: number;
  total_reste_du: number;
  taux_paiement: number;
  jours_depuis_dernier_achat: number;
}

interface ClassificationResult {
  supplier_id: number;
  supplier_name: string;
  segment: number; // 0=En Risque, 1=Standard, 2=Clé
  prediction_label: string;
  probability: number;
  confidence_level: string;
  features_used: {
    nb_factures: number;
    nb_produits_differents: number;
    montant_total_ht: number;
    taux_paiement: number;
    nb_mois_actifs: number;
    jours_depuis_dernier_achat: number;
  };
  analysis: {
    strengths: string[];
    weaknesses: string[];
    recommendation: string;
  };
  model: string;
  timestamp: string;
}

@Component({
  selector: 'app-supplier-classification',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './supplier-classification.component.html',
  styleUrl: './supplier-classification.component.css'
})
export class SupplierClassificationComponent implements OnInit, OnDestroy {
  suppliers = signal<Supplier[]>([]);
  filteredSuppliers = signal<Supplier[]>([]);
  selectedSupplier = signal<Supplier | null>(null);
  classificationResult = signal<ClassificationResult | null>(null);
  isLoadingSuppliers = signal<boolean>(false);
  isClassifying = signal<boolean>(false);
  isSearching = signal<boolean>(false);
  errorMessage = signal<string>('');
  searchTerm = '';
  private searchTimer: any = null;

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    public translate: TranslationService,
    private notif: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadSuppliers();
  }

  ngOnDestroy(): void {
    if (this.searchTimer) clearTimeout(this.searchTimer);
  }

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  loadSuppliers(): void {
    this.isLoadingSuppliers.set(true);
    this.errorMessage.set('');

    this.http.get<{suppliers: Supplier[], count: number}>(`${environment.apiUrl}/ml/iyadh/suppliers`, {
      headers: this.getHeaders()
    }).subscribe({
      next: (response) => {
        this.suppliers.set(response.suppliers);
        this.filteredSuppliers.set(response.suppliers);
        this.isLoadingSuppliers.set(false);
      },
      error: (error) => {
        console.error('Erreur lors du chargement des fournisseurs:', error);
        this.errorMessage.set(error.error?.error || 'Erreur lors du chargement des fournisseurs');
        this.isLoadingSuppliers.set(false);
        this.notif.error('Erreur lors du chargement des fournisseurs');
      }
    });
  }

  onSearchChange(): void {
    this.isSearching.set(true);
    
    if (this.searchTimer) clearTimeout(this.searchTimer);
    
    this.searchTimer = setTimeout(() => {
      const term = this.searchTerm.toLowerCase().trim();
      
      if (!term) {
        this.filteredSuppliers.set(this.suppliers());
      } else {
        const filtered = this.suppliers().filter(supplier =>
          supplier.nom.toLowerCase().includes(term) ||
          supplier.matricule_fiscal?.toLowerCase().includes(term)
        );
        this.filteredSuppliers.set(filtered);
      }
      
      this.isSearching.set(false);
    }, 300);
  }

  clearSearch(): void {
    this.searchTerm = '';
    this.filteredSuppliers.set(this.suppliers());
  }

  selectSupplier(supplier: Supplier): void {
    this.selectedSupplier.set(supplier);
    this.classificationResult.set(null);
    this.errorMessage.set('');
  }

  classifySupplier(): void {
    const supplier = this.selectedSupplier();
    if (!supplier) {
      this.errorMessage.set('Veuillez sélectionner un fournisseur');
      return;
    }

    this.isClassifying.set(true);
    this.errorMessage.set('');

    const requestData = {
      supplier_id: supplier.id,
      lang: this.translate.currentLanguage()
    };

    this.http.post<ClassificationResult>(`${environment.apiUrl}/ml/iyadh/classify-supplier`, requestData, {
      headers: this.getHeaders()
    }).subscribe({
      next: (result) => {
        this.classificationResult.set(result);
        this.isClassifying.set(false);
        
        if (result.segment === 2) {
          this.notif.success(this.translate.translate('supplierClassification.segmentCle'));
        } else if (result.segment === 1) {
          this.notif.info(this.translate.translate('supplierClassification.segmentStandard'));
        } else {
          this.notif.warning(this.translate.translate('supplierClassification.segmentRisque'));
        }
      },
      error: (error) => {
        console.error('Erreur lors de la classification:', error);
        this.errorMessage.set(error.error?.error || 'Erreur lors de la classification');
        this.isClassifying.set(false);
        this.notif.error('Erreur lors de la classification');
      }
    });
  }

  getPaymentRateClass(rate: number): string {
    if (rate >= 80) return 'rate-excellent';
    if (rate >= 60) return 'rate-good';
    if (rate >= 40) return 'rate-warning';
    return 'rate-danger';
  }

  getRecencyClass(days: number): string {
    if (days < 30) return 'recency-excellent';
    if (days < 90) return 'recency-good';
    if (days < 180) return 'recency-warning';
    return 'recency-danger';
  }

  getSegmentClass(segment: number): string {
    switch (segment) {
      case 2: return 'segment-cle';
      case 1: return 'segment-standard';
      default: return 'segment-risque';
    }
  }

  getSegmentIcon(segment: number): string {
    switch (segment) {
      case 2: return '🔑';
      case 1: return '📋';
      default: return '⚠️';
    }
  }
}