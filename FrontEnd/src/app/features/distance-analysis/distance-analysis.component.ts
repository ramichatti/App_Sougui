import { Component } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from '../../core/services/auth.service';
import { TranslationService } from '../../core/services/translation.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-distance-analysis',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './distance-analysis.component.html',
  styleUrls: ['./distance-analysis.component.css']
})
export class DistanceAnalysisComponent {
  // Liste des entreprises avec coordonnées CORRIGÉES
  entreprises = [
    { id: 1, nom: "Attijari Alyssa Sokra", lat: 36.833328, lon: 10.250000 },
    { id: 2, nom: "Attijari Groupe oasis", lat: 35.678101, lon: 10.096900 },      // ← ÉCHANGÉ
    { id: 3, nom: "Attijari Groupe Al Aghaliba", lat: 33.883461, lon: 10.098180 }, // ← ÉCHANGÉ
    { id: 4, nom: "Tunis Call Center", lat: 36.800205, lon: 10.185776 },
    { id: 5, nom: "WIFAK BANK", lat: 36.800205, lon: 10.185776 },
    { id: 6, nom: "Lilas", lat: 36.861401, lon: 10.329005 },
    { id: 7, nom: "TTE INTERNATIONAL", lat: 37.272091, lon: 9.870857 },
    { id: 8, nom: "SBCD", lat: 36.800205, lon: 10.185776 }
  ];

  souguiLat = 36.7682;
  souguiLon = 10.2356;

  selectedEntreprise: any = null;
  analysisResult: any = null;
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
    this.analysisResult = null;
    this.errorMessage = '';
  }

  analyzeDistance() {
    if (!this.selectedEntreprise) {
      this.errorMessage = this.translate.translate('common.selectOption');
      return;
    }

    this.isLoading = true;
    this.analysisResult = null;
    this.errorMessage = '';

    const body = {
      lat1: this.souguiLat,
      lon1: this.souguiLon,
      lat2: this.selectedEntreprise.lat,
      lon2: this.selectedEntreprise.lon
    };

    this.http.post(`${environment.apiUrl}/delivery/distance`, body, {
      headers: this.getHeaders()
    }).subscribe({
      next: (response: any) => {
        const distance = response.distance_km;
        const isProche = distance <= 30;
        
        this.analysisResult = {
          entreprise: this.selectedEntreprise.nom,
          distance: distance,
          isProche: isProche,
          classification: isProche ? '🟢 ' + this.translate.translate('distance.closeClient') : '🔴 ' + this.translate.translate('distance.farClient'),
          zone: isProche ? this.translate.translate('distance.proximityZone') : this.translate.translate('distance.distantZone'),
          message: isProche 
            ? this.translate.translate('distance.fastDelivery')
            : this.translate.translate('distance.longDelivery'),
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