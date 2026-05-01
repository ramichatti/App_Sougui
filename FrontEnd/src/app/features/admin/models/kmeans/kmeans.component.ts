import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { NavbarComponent } from '../../../../shared/components/navbar/navbar.component';
import { environment } from '../../../../../environments/environment';

interface KMeansResult {
  cluster: number;
  cluster_name: string;
  cluster_centers: number[][];
  distance_to_center: number;
  n_clusters: number;
  input_features: {
    recency: number;
    frequency: number;
    monetary: number;
    panier_moyen: number;
    quantite_totale: number;
    taux_reduction: number;
    produits_par_commande: number;
  };
  feature_names: string[];
}

@Component({
  selector: 'app-kmeans',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, NavbarComponent],
  templateUrl: './kmeans.component.html',
  styleUrls: ['./kmeans.component.css']
})
export class KmeansComponent {
  // Input features with real names
  recency = '';
  frequency = '';
  monetary = '';
  panier_moyen = '';
  quantite_totale = '';
  taux_reduction = '';
  produits_par_commande = '';

  // State
  isLoading = signal(false);
  result = signal<KMeansResult | null>(null);
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
      recency: parseFloat(this.recency),
      frequency: parseInt(this.frequency),
      monetary: parseFloat(this.monetary),
      panier_moyen: parseFloat(this.panier_moyen),
      quantite_totale: parseFloat(this.quantite_totale),
      taux_reduction: parseFloat(this.taux_reduction),
      produits_par_commande: parseFloat(this.produits_par_commande)
    };

    this.http.post<KMeansResult>(`${this.apiUrl}/ml-models/balkis/kmeans`, payload)
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
      this.recency && !isNaN(parseFloat(this.recency)) && parseFloat(this.recency) >= 0 &&
      this.frequency && !isNaN(parseInt(this.frequency)) && parseInt(this.frequency) >= 0 &&
      this.monetary && !isNaN(parseFloat(this.monetary)) && parseFloat(this.monetary) >= 0 &&
      this.panier_moyen && !isNaN(parseFloat(this.panier_moyen)) && parseFloat(this.panier_moyen) >= 0 &&
      this.quantite_totale && !isNaN(parseFloat(this.quantite_totale)) && parseFloat(this.quantite_totale) >= 0 &&
      this.taux_reduction !== '' && !isNaN(parseFloat(this.taux_reduction)) && parseFloat(this.taux_reduction) >= 0 && parseFloat(this.taux_reduction) <= 1 &&
      this.produits_par_commande && !isNaN(parseFloat(this.produits_par_commande)) && parseFloat(this.produits_par_commande) >= 0
    );
  }

  reset(): void {
    this.recency = '';
    this.frequency = '';
    this.monetary = '';
    this.panier_moyen = '';
    this.quantite_totale = '';
    this.taux_reduction = '';
    this.produits_par_commande = '';
    this.result.set(null);
    this.errorMsg.set('');
  }

  goBack(): void {
    this.router.navigate(['/admin/models']);
  }
}
