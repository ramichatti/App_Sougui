import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { MlPredictionService, Product, PredictionResponse, ModelInfo } from '../../../core/services/ml-prediction.service';
import { TranslationService } from '../../../core/services/translation.service';

@Component({
  selector: 'app-ml-models',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent],
  templateUrl: './ml-models.component.html',
  styleUrls: ['./ml-models.component.css']
})
export class MlModelsComponent implements OnInit {
  products = signal<Product[]>([]);
  selectedProduct = signal<Product | null>(null);
  predictions = signal<PredictionResponse | null>(null);
  modelInfo = signal<ModelInfo | null>(null);
  
  isLoading = signal<boolean>(false);
  isLoadingProducts = signal<boolean>(true);
  isLoadingPrediction = signal<boolean>(false);
  
  searchTerm = signal<string>('');
  selectedCategory = signal<string>('all');
  
  // Pagination
  currentPage = signal<number>(1);
  itemsPerPage = 9; // 3x3 grid

  // Computed values
  filteredProducts = computed(() => {
    let filtered = this.products();
    
    // Filter by category
    if (this.selectedCategory() !== 'all') {
      filtered = filtered.filter(p => p.Produit_Categorie === this.selectedCategory());
    }
    
    // Filter by search term (prioritize name search)
    const search = this.searchTerm().trim();
    if (search) {
      const searchLower = search.toLowerCase();
      filtered = filtered.filter(p => {
        const nameMatch = p.Produit_Nom.toLowerCase().includes(searchLower);
        const refMatch = p.Produit_Reference.toLowerCase().includes(searchLower);
        const descMatch = p.Produit_Description.toLowerCase().includes(searchLower);
        
        // Prioritize name matches
        return nameMatch || refMatch || descMatch;
      });
      
      // Sort by relevance: name matches first
      filtered = filtered.sort((a, b) => {
        const aNameMatch = a.Produit_Nom.toLowerCase().includes(searchLower);
        const bNameMatch = b.Produit_Nom.toLowerCase().includes(searchLower);
        
        if (aNameMatch && !bNameMatch) return -1;
        if (!aNameMatch && bNameMatch) return 1;
        
        // If both match or both don't match, sort alphabetically by name
        return a.Produit_Nom.localeCompare(b.Produit_Nom);
      });
    }
    
    return filtered;
  });

  // Paginated products
  paginatedProducts = computed(() => {
    const filtered = this.filteredProducts();
    const start = (this.currentPage() - 1) * this.itemsPerPage;
    const end = start + this.itemsPerPage;
    return filtered.slice(start, end);
  });

  // Total pages
  totalPages = computed(() => {
    return Math.ceil(this.filteredProducts().length / this.itemsPerPage);
  });

  // Page numbers for pagination UI
  pageNumbers = computed(() => {
    const total = this.totalPages();
    const current = this.currentPage();
    const pages: number[] = [];
    
    if (total <= 7) {
      // Show all pages if 7 or less
      for (let i = 1; i <= total; i++) {
        pages.push(i);
      }
    } else {
      // Always show first page
      pages.push(1);
      
      if (current > 3) {
        pages.push(-1); // Ellipsis
      }
      
      // Show pages around current
      for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
        pages.push(i);
      }
      
      if (current < total - 2) {
        pages.push(-1); // Ellipsis
      }
      
      // Always show last page
      pages.push(total);
    }
    
    return pages;
  });

  categories = computed(() => {
    const cats = new Set(this.products().map(p => p.Produit_Categorie));
    return Array.from(cats).sort();
  });

  constructor(
    private mlService: MlPredictionService,
    public translate: TranslationService
  ) {}

  ngOnInit(): void {
    this.loadProducts();
    this.loadModelInfo();
  }

  loadProducts(): void {
    this.isLoadingProducts.set(true);
    this.mlService.getProducts().subscribe({
      next: (response) => {
        this.products.set(response.products || []);
        this.isLoadingProducts.set(false);
      },
      error: (error) => {
        console.error('Error loading products:', error);
        this.isLoadingProducts.set(false);
        alert('Erreur lors du chargement des produits');
      }
    });
  }

  loadModelInfo(): void {
    this.mlService.getModelInfo().subscribe({
      next: (info) => {
        this.modelInfo.set(info);
      },
      error: (error) => {
        console.error('Error loading model info:', error);
      }
    });
  }

  selectProduct(product: Product): void {
    this.selectedProduct.set(product);
    this.predictions.set(null);
  }

  predictDemand(): void {
    const product = this.selectedProduct();
    if (!product) return;

    this.isLoadingPrediction.set(true);
    this.mlService.predictDemand(product.Id_Produit).subscribe({
      next: (response) => {
        this.predictions.set(response);
        this.isLoadingPrediction.set(false);
      },
      error: (error) => {
        console.error('Error predicting demand:', error);
        this.isLoadingPrediction.set(false);
        
        // Gestion spécifique des erreurs
        if (error.status === 400 && error.error?.available_months !== undefined) {
          const available = error.error.available_months;
          const required = error.error.required_months || 3;
          alert(`❌ Données insuffisantes pour ce produit\n\n` +
                `Ce produit a seulement ${available} mois d'historique.\n` +
                `Au moins ${required} mois sont nécessaires pour générer des prédictions fiables.\n\n` +
                `💡 Conseil: Choisissez un produit avec plus d'historique de ventes.`);
        } else {
          const errorMsg = error.error?.message || error.error?.error || 'Erreur lors de la prédiction';
          alert(`❌ ${errorMsg}`);
        }
      }
    });
  }

  clearSelection(): void {
    this.selectedProduct.set(null);
    this.predictions.set(null);
  }

  // Pagination methods
  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages()) {
      this.currentPage.set(page);
      // Scroll to products grid
      const productsGrid = document.querySelector('.products-grid');
      if (productsGrid) {
        productsGrid.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }

  nextPage(): void {
    if (this.currentPage() < this.totalPages()) {
      this.goToPage(this.currentPage() + 1);
    }
  }

  previousPage(): void {
    if (this.currentPage() > 1) {
      this.goToPage(this.currentPage() - 1);
    }
  }

  // Reset to page 1 when filters change
  onSearchChange(value: string): void {
    this.searchTerm.set(value);
    this.currentPage.set(1);
  }

  clearSearch(): void {
    this.searchTerm.set('');
    this.currentPage.set(1);
  }

  onCategoryChange(category: string): void {
    this.selectedCategory.set(category);
    this.currentPage.set(1);
  }

  getMonthColor(index: number): string {
    const colors = ['#3b82f6', '#8b5cf6', '#ec4899'];
    return colors[index % colors.length];
  }

  getTotalPredicted(): number {
    const preds = this.predictions();
    if (!preds) return 0;
    return preds.predictions.reduce((sum, p) => sum + p.predicted_quantity, 0);
  }

  formatNumber(num: number): string {
    return new Intl.NumberFormat('fr-FR', { 
      minimumFractionDigits: 0,
      maximumFractionDigits: 2 
    }).format(num);
  }

  formatCurrency(num: number): string {
    return new Intl.NumberFormat('fr-FR', { 
      style: 'currency', 
      currency: 'TND' 
    }).format(num);
  }

  getTrendIcon(direction: string): string {
    switch(direction) {
      case 'croissante':
      case 'rising':
        return '↗';
      case 'décroissante':
      case 'falling':
        return '↘';
      default: return '→';
    }
  }

  getTrendColor(direction: string): string {
    switch(direction) {
      case 'croissante':
      case 'rising':
        return '#16a34a';
      case 'décroissante':
      case 'falling':
        return '#dc2626';
      default: return '#64748b';
    }
  }

  getConfidenceColor(confidence: number): string {
    if (confidence >= 80) return '#16a34a';
    if (confidence >= 65) return '#3b82f6';
    return '#f59e0b';
  }

  getDataQualityBadge(quality: string): { text: string; color: string } {
    const lang = this.translate.currentLanguage();
    switch(quality) {
      case 'excellent': return { 
        text: lang === 'fr' ? 'Excellente' : 'Excellent', 
        color: '#16a34a' 
      };
      case 'good': return { 
        text: lang === 'fr' ? 'Bonne' : 'Good', 
        color: '#3b82f6' 
      };
      default: return { 
        text: lang === 'fr' ? 'Acceptable' : 'Acceptable', 
        color: '#f59e0b' 
      };
    }
  }

  getVolatilityLabel(volatility: number): string {
    const lang = this.translate.currentLanguage();
    if (volatility < 30) return lang === 'fr' ? 'Faible' : 'Low';
    if (volatility < 60) return lang === 'fr' ? 'Modérée' : 'Moderate';
    return lang === 'fr' ? 'Élevée' : 'High';
  }

  getTrendLabel(direction: string): string {
    const lang = this.translate.currentLanguage();
    if (lang === 'en') {
      switch(direction) {
        case 'croissante': return 'Rising';
        case 'décroissante': return 'Falling';
        case 'stable': return 'Stable';
        default: return direction;
      }
    }
    return direction.charAt(0).toUpperCase() + direction.slice(1);
  }
}
