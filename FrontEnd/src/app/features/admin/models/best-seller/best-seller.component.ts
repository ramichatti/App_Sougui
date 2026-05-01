import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { NavbarComponent } from '../../../../shared/components/navbar/navbar.component';
import { environment } from '../../../../../environments/environment';

interface BestSellerResult {
  prediction: number;
  score: number;
  status: string;
  status_class: string;
  input_features: {
    prix_moyen: number;
    quantite_moyenne: number;
    nombre_commandes: number;
    taux_reduction: number;
    velocite_ventes: number;
    categorie_prix: number;
  };
}

@Component({
  selector: 'app-best-seller',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, NavbarComponent],
  templateUrl: './best-seller.component.html',
  styleUrls: ['./best-seller.component.css']
})
export class BestSellerComponent {
  // Input features with real names
  prix_moyen = '';
  quantite_moyenne = '';
  nombre_commandes = '';
  taux_reduction = '';
  velocite_ventes = '';
  categorie_prix = '';

  // State
  isLoading = signal(false);
  result = signal<BestSellerResult | null>(null);
  errorMsg = signal('');

  private apiUrl = environment.apiUrl;

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  predict(): void {
    if (!this.validateInputs()) {
      this.errorMsg.set('Veuillez remplir tous les champs avec des valeurs valides');
      return;
    }

    this.isLoading.set(true);
    this.errorMsg.set('');
    this.result.set(null);

    const payload = {
      prix_moyen: parseFloat(this.prix_moyen),
      quantite_moyenne: parseFloat(this.quantite_moyenne),
      nombre_commandes: parseInt(this.nombre_commandes),
      taux_reduction: parseFloat(this.taux_reduction),
      velocite_ventes: parseFloat(this.velocite_ventes),
      categorie_prix: parseInt(this.categorie_prix)
    };

    this.http.post<BestSellerResult>(`${this.apiUrl}/ml-models/balkis/best-seller`, payload)
      .subscribe({
        next: (response) => {
          this.isLoading.set(false);
          this.result.set(response);
        },
        error: (err) => {
          this.isLoading.set(false);
          this.errorMsg.set(err.error?.error || 'Erreur lors de la prédiction');
        }
      });
  }

  validateInputs(): boolean {
    return !!(
      this.prix_moyen && !isNaN(parseFloat(this.prix_moyen)) && parseFloat(this.prix_moyen) >= 0 &&
      this.quantite_moyenne && !isNaN(parseFloat(this.quantite_moyenne)) && parseFloat(this.quantite_moyenne) >= 0 &&
      this.nombre_commandes && !isNaN(parseInt(this.nombre_commandes)) && parseInt(this.nombre_commandes) >= 0 &&
      this.taux_reduction !== '' && !isNaN(parseFloat(this.taux_reduction)) && parseFloat(this.taux_reduction) >= 0 && parseFloat(this.taux_reduction) <= 1 &&
      this.velocite_ventes && !isNaN(parseFloat(this.velocite_ventes)) && parseFloat(this.velocite_ventes) >= 0 &&
      this.categorie_prix && !isNaN(parseInt(this.categorie_prix)) && parseInt(this.categorie_prix) >= 1
    );
  }

  reset(): void {
    this.prix_moyen = '';
    this.quantite_moyenne = '';
    this.nombre_commandes = '';
    this.taux_reduction = '';
    this.velocite_ventes = '';
    this.categorie_prix = '';
    this.result.set(null);
    this.errorMsg.set('');
  }

  goBack(): void {
    this.router.navigate(['/admin/models']);
  }

  getStatusColor(statusClass: string): string {
    switch(statusClass) {
      case 'excellent': return '#10b981';
      case 'good': return '#3b82f6';
      case 'medium': return '#f59e0b';
      case 'low': return '#ef4444';
      default: return '#6b7280';
    }
  }

  getStatusGradient(statusClass: string): string {
    switch(statusClass) {
      case 'excellent': return 'linear-gradient(135deg, #d1fae5, #a7f3d0)';
      case 'good': return 'linear-gradient(135deg, #dbeafe, #bfdbfe)';
      case 'medium': return 'linear-gradient(135deg, #fef3c7, #fde68a)';
      case 'low': return 'linear-gradient(135deg, #fee2e2, #fecaca)';
      default: return 'linear-gradient(135deg, #f3f4f6, #e5e7eb)';
    }
  }
}
