import { Component, OnInit, signal, OnDestroy } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from '../../core/services/auth.service';
import { TranslationService } from '../../core/services/translation.service';
import { NotificationService } from '../../core/services/notification.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';

interface Product {
  Id_Produit: number;
  Produit_Reference: string;
  Produit_Nom: string;
  Produit_Description: string;
  Produit_Categorie: string;
  Produit_PU_HT: number;
  Produit_Source?: string;
  Produit_En_Stock?: number;
  Nb_Ventes?: number;
}

interface BestSellerResult {
  product_id: number;
  is_best_seller: boolean;
  best_seller_probability: number;
  prediction_label: string;
  features_used: {
    total_qty: number;
    nb_commandes: number;
    nb_clients: number;
    ca_ht: number;
    avg_qty: number;
    pu_ht: number;
    lag_1: number;
    lag_2: number;
    lag_3: number;
    rolling_mean_3: number;
  };
  model: string;
  timestamp: string;
}

@Component({
  selector: 'app-best-seller-b2c',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './best-seller-b2c.component.html',
  styleUrls: ['./best-seller-b2c.component.css']
})
export class BestSellerB2cComponent implements OnInit, OnDestroy {
  products = signal<Product[]>([]);
  filteredProducts = signal<Product[]>([]);
  selectedProduct = signal<Product | null>(null);
  predictionResult = signal<BestSellerResult | null>(null);
  isLoadingProducts = signal<boolean>(false);
  isPredicting = signal<boolean>(false);
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
    this.loadProducts();
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

  loadProducts(): void {
    this.isLoadingProducts.set(true);
    this.errorMessage.set('');

    this.http.get<{ products: Product[]; count: number }>(`${environment.apiUrl}/ml/dwh/products?limit=200`, {
      headers: this.getHeaders()
    }).subscribe({
      next: (response) => {
        this.products.set(response.products);
        this.filteredProducts.set(response.products);
        this.isLoadingProducts.set(false);
      },
      error: (error) => {
        console.error('Error loading products:', error);
        this.errorMessage.set(error.error?.error || 'Error loading products');
        this.isLoadingProducts.set(false);
        this.notif.error('Error loading products');
      }
    });
  }

  onSearchChange(): void {
    if (this.searchTimer) clearTimeout(this.searchTimer);

    const term = this.searchTerm.trim();
    if (!term) {
      this.filteredProducts.set(this.products());
      this.isSearching.set(false);
      return;
    }

    this.isSearching.set(true);
    this.searchTimer = setTimeout(() => {
      this.http.get<{ products: Product[]; count: number }>(
        `${environment.apiUrl}/ml/dwh/products?search=${encodeURIComponent(term)}&limit=50`,
        { headers: this.getHeaders() }
      ).subscribe({
        next: (response) => {
          this.filteredProducts.set(response.products);
          this.isSearching.set(false);
        },
        error: () => {
          const t = term.toLowerCase();
          const filtered = this.products().filter(p =>
            p.Produit_Reference.toLowerCase().includes(t) ||
            p.Produit_Nom.toLowerCase().includes(t) ||
            p.Produit_Description.toLowerCase().includes(t)
          );
          this.filteredProducts.set(filtered);
          this.isSearching.set(false);
        }
      });
    }, 300);
  }

  clearSearch(): void {
    this.searchTerm = '';
    this.filteredProducts.set(this.products());
    this.isSearching.set(false);
  }

  selectProduct(product: Product): void {
    this.selectedProduct.set(product);
    this.predictionResult.set(null);
    this.errorMessage.set('');
  }

  predictBestSeller(): void {
    const product = this.selectedProduct();
    if (!product) {
      this.errorMessage.set('Please select a product');
      return;
    }

    this.isPredicting.set(true);
    this.errorMessage.set('');
    this.predictionResult.set(null);

    const body = { product_id: product.Id_Produit };

    this.http.post<BestSellerResult>(`${environment.apiUrl}/ml/balkis/best-seller-b2c`, body, {
      headers: this.getHeaders()
    }).subscribe({
      next: (response) => {
        this.predictionResult.set(response);
        this.isPredicting.set(false);
        this.notif.success('Prediction completed successfully');
      },
      error: (error) => {
        console.error('Prediction error:', error);
        this.errorMessage.set(error.error?.error || 'Prediction failed');
        this.isPredicting.set(false);
        this.notif.error('Prediction failed');
      }
    });
  }

  clearSelection(): void {
    this.selectedProduct.set(null);
    this.predictionResult.set(null);
    this.errorMessage.set('');
  }

  getProbColor(prob: number): string {
    if (prob >= 70) return '#16a34a';
    if (prob >= 40) return '#f59e0b';
    return '#ef4444';
  }

  getProbLabel(prob: number): string {
    if (prob >= 70) return this.translate.translate('bestSeller.high');
    if (prob >= 40) return this.translate.translate('bestSeller.medium');
    return this.translate.translate('bestSeller.low');
  }
}
