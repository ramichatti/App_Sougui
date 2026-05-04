import { Component } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from '../../core/services/auth.service';
import { TranslationService } from '../../core/services/translation.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-predict-cost',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './predict-cost.component.html',
  styleUrls: ['./predict-cost.component.css']
})
export class PredictCostComponent {
  // Liste des entreprises avec distances
  entreprises = [
    { id: 1, nom: "Attijari Alyssa Sokra", distance: 7.35 },
    { id: 2, nom: "Attijari Groupe oasis", distance: 121.85 },
    { id: 3, nom: "Attijari Groupe Al Aghaliba", distance: 321.01 },
    { id: 4, nom: "Tunis Call Center", distance: 5.69 },
    { id: 5, nom: "WIFAK BANK", distance: 5.69 },
    { id: 6, nom: "Lilas", distance: 13.29 },
    { id: 7, nom: "TTE INTERNATIONAL", distance: 64.71 },
    { id: 8, nom: "SBCD", distance: 5.69 }
  ];

  selectedEntreprise: any = null;
  predictionResult: any = null;
  isLoading: boolean = false;
  errorMessage: string = '';

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    public translate: TranslationService
  ) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  onEntrepriseChange(event: any) {
    const id = parseInt(event.target.value);
    this.selectedEntreprise = this.entreprises.find(e => e.id === id);
    this.predictionResult = null;
    this.errorMessage = '';
  }

  predictCost() {
    if (!this.selectedEntreprise) {
      this.errorMessage = this.translate.translate('common.selectOption');
      return;
    }

    this.isLoading = true;
    this.predictionResult = null;
    this.errorMessage = '';

    const body = { distance_km: this.selectedEntreprise.distance };

    this.http.post(`${environment.apiUrl}/delivery/predict/cout`, body, {
      headers: this.getHeaders()
    }).subscribe({
      next: (response: any) => {
        this.predictionResult = {
          cout: response.cout_predit,
          distance: this.selectedEntreprise.distance,
          entreprise: this.selectedEntreprise.nom,
          timestamp: new Date()
        };
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Erreur:', error);
        this.errorMessage = error.error?.error || this.translate.translate('common.connectionError');
        this.isLoading = false;
      }
    });
  }
}