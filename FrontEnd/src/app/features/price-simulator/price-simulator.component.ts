import { Component, OnInit, signal, OnDestroy } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from '../../core/services/auth.service';
import { TranslationService } from '../../core/services/translation.service';
import { NotificationService } from '../../core/services/notification.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';

interface Product {
  id: number;
  reference: string;
  name: string;
  sougui_price: number;
  kalys_price?: number;
  ileycom_price?: number;
  avg_competitor_price?: number;
  position: string;
  in_stock: number;
}

interface PriceSimulationResult {
  product_reference: string;
  product_name: string;
  current_price: number;
  new_price: number;
  price_change: number;
  price_change_percentage: number;
  competitor_prices: {
    kalys_price?: number;
    ileycom_price?: number;
    average_competitor_price: number;
  };
  competitiveness_analysis: {
    price_difference_vs_competitors: number;
    position: string;
    competitiveness: string;
    competitiveness_score: number;
    price_segment: string;
    segment_strategy: string;
  };
  ml_predictions: {
    current_prediction: number;
    new_prediction: number;
    current_probability: number[];
    new_probability: number[];
    interpretation: string;
  };
  business_impact: {
    revenue_impact_per_100_units: number;
    competitiveness_score_impact: number;
    demand_change_percentage: number;
    estimated_new_volume: number;
    margin_analysis: {
      current_margin: number;
      new_margin: number;
      margin_change: number;
      margin_change_percentage: number;
    };
  };
  recommendation: {
    message: string;
    type: string;
  };
  risk_analysis: {
    risks: string[];
    opportunities: string[];
  };
  model: string;
  timestamp: string;
}

@Component({
  selector: 'app-price-simulator',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './price-simulator.component.html',
  styleUrl: './price-simulator.component.css'
})
export class PriceSimulatorComponent implements OnInit, OnDestroy {
  products = signal<Product[]>([]);
  filteredProducts = signal<Product[]>([]);
  selectedProduct = signal<Product | null>(null);
  simulationResult = signal<PriceSimulationResult | null>(null);
  isLoadingProducts = signal<boolean>(false);
  isSimulating = signal<boolean>(false);
  isSearching = signal<boolean>(false);
  errorMessage = signal<string>('');
  searchTerm = '';
  newPrice = 0;
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

    this.http.get<{products: Product[], count: number}>(`${environment.apiUrl}/ml/elyes/products`, {
      headers: this.getHeaders()
    }).subscribe({
      next: (response) => {
        this.products.set(response.products);
        this.filteredProducts.set(response.products);
        this.isLoadingProducts.set(false);
      },
      error: (error) => {
        console.error('Erreur lors du chargement des produits:', error);
        this.errorMessage.set(error.error?.error || 'Erreur lors du chargement des produits');
        this.isLoadingProducts.set(false);
        this.notif.error('Erreur lors du chargement des produits');
      }
    });
  }

  onSearchChange(): void {
    this.isSearching.set(true);
    
    if (this.searchTimer) clearTimeout(this.searchTimer);
    
    this.searchTimer = setTimeout(() => {
      const term = this.searchTerm.toLowerCase().trim();
      
      if (!term) {
        this.filteredProducts.set(this.products());
      } else {
        const filtered = this.products().filter(product =>
          product.reference.toLowerCase().includes(term) ||
          product.name.toLowerCase().includes(term)
        );
        this.filteredProducts.set(filtered);
      }
      
      this.isSearching.set(false);
    }, 300);
  }

  selectProduct(product: Product): void {
    this.selectedProduct.set(product);
    this.newPrice = product.sougui_price;
    this.simulationResult.set(null);
    this.errorMessage.set('');
  }

  onPriceChange(event: any): void {
    this.newPrice = parseFloat(event.target.value) || 0;
    // Auto-simulate when price changes (with debounce)
    if (this.selectedProduct() && this.newPrice > 0) {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        this.simulatePrice();
      }, 500);
    }
  }

  simulatePrice(): void {
    const product = this.selectedProduct();
    if (!product || this.newPrice <= 0) {
      this.errorMessage.set('Veuillez sélectionner un produit et saisir un prix valide');
      return;
    }

    this.isSimulating.set(true);
    this.errorMessage.set('');

    const requestData = {
      product_reference: product.reference,
      new_price: this.newPrice
    };

    this.http.post<PriceSimulationResult>(`${environment.apiUrl}/ml/elyes/price-simulator`, requestData, {
      headers: this.getHeaders()
    }).subscribe({
      next: (result) => {
        this.simulationResult.set(result);
        this.isSimulating.set(false);
      },
      error: (error) => {
        console.error('Erreur lors de la simulation:', error);
        this.errorMessage.set(error.error?.error || 'Erreur lors de la simulation');
        this.isSimulating.set(false);
        this.notif.error('Erreur lors de la simulation de prix');
      }
    });
  }

  getPositionClass(position: string): string {
    switch (position) {
      case 'Much_Cheaper':
      case 'Cheaper': 
      case 'Slightly_Cheaper': return 'badge-success';
      case 'Similar_Price': return 'badge-info';
      case 'Slightly_More_Expensive': return 'badge-warning';
      case 'More_Expensive':
      case 'Much_More_Expensive': return 'badge-danger';
      case 'Competitive': return 'badge-success';
      default: return 'badge-secondary';
    }
  }

  getPositionText(position: string): string {
    switch (position) {
      case 'Much_Cheaper': return 'Très Avantageux';
      case 'Cheaper': return 'Moins Cher';
      case 'Slightly_Cheaper': return 'Légèrement Moins Cher';
      case 'Similar_Price': return 'Prix Similaire';
      case 'Slightly_More_Expensive': return 'Légèrement Plus Cher';
      case 'More_Expensive': return 'Plus Cher';
      case 'Much_More_Expensive': return 'Très Cher';
      case 'Competitive': return 'Compétitif';
      case 'No_Competition': return 'Pas de Concurrence';
      default: return position;
    }
  }

  getRecommendationClass(type: string): string {
    switch (type) {
      case 'excellent': return 'alert-success';
      case 'good': return 'alert-info';
      case 'warning': return 'alert-warning';
      case 'danger': return 'alert-danger';
      default: return 'alert-secondary';
    }
  }

  clearSearch(): void {
    this.searchTerm = '';
    this.filteredProducts.set(this.products());
  }
}