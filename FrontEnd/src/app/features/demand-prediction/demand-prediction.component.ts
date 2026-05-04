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

interface PredictionResult {
  month1: { month: string; quantity: number; };
  month2: { month: string; quantity: number; };
  month3: { month: string; quantity: number; };
  total: number;
  product: Product;
  timestamp: Date;
}

@Component({
  selector: 'app-demand-prediction',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './demand-prediction.component.html',
  styleUrls: ['./demand-prediction.component.css']
})
export class DemandPredictionComponent implements OnInit, OnDestroy {
  products = signal<Product[]>([]);
  filteredProducts = signal<Product[]>([]);
  selectedProduct = signal<Product | null>(null);
  predictionResult = signal<PredictionResult | null>(null);
  isLoading = signal<boolean>(false);
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

    // Debounced server-side search via DWH API (searches by Nom, Reference, Description)
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
          // Fallback to client-side filter
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

  predictDemand(): void {
    const product = this.selectedProduct();
    if (!product) {
      this.errorMessage.set('Please select a product');
      return;
    }

    this.isPredicting.set(true);
    this.errorMessage.set('');
    this.predictionResult.set(null);

    const body = {
      product_id: product.Id_Produit,
      product_reference: product.Produit_Reference,
      product_description: product.Produit_Description,
      product_pu_ht: product.Produit_PU_HT
    };

    this.http.post<any>(`${environment.apiUrl}/ml/rami/predict-demand`, body, {
      headers: this.getHeaders()
    }).subscribe({
      next: (response) => {
        const now = new Date();
        const predictions = response.predictions || [];
        
        this.predictionResult.set({
          month1: predictions[0] || { month: this.getMonthName(now, 1), quantity: 0 },
          month2: predictions[1] || { month: this.getMonthName(now, 2), quantity: 0 },
          month3: predictions[2] || { month: this.getMonthName(now, 3), quantity: 0 },
          total: (predictions[0]?.quantity || 0) + (predictions[1]?.quantity || 0) + (predictions[2]?.quantity || 0),
          product: product,
          timestamp: new Date()
        });
        
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

  private getMonthName(date: Date, offset: number): string {
    const newDate = new Date(date);
    newDate.setMonth(newDate.getMonth() + offset);
    const monthNames = this.translate.currentLanguage() === 'fr' 
      ? ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
      : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `${monthNames[newDate.getMonth()]} ${newDate.getFullYear()}`;
  }

  maxQuantity(): number {
    const r = this.predictionResult();
    if (!r) return 1;
    return Math.max(r.month1.quantity, r.month2.quantity, r.month3.quantity, 1);
  }

  barHeight(qty: number): number {
    return Math.max(8, (qty / this.maxQuantity()) * 100);
  }

  clearSelection(): void {
    this.selectedProduct.set(null);
    this.predictionResult.set(null);
    this.errorMessage.set('');
  }
}
