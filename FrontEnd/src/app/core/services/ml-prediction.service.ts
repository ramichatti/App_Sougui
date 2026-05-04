import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Product {
  Id_Produit: number;
  Produit_Reference: string;
  Produit_Description: string;
  Produit_Nom: string;
  Produit_PU_HT: number;
  Produit_Categorie: string;
  history_months?: number;
  has_sufficient_data?: boolean;
}

export interface Prediction {
  month: number;
  year: number;
  month_name: string;
  predicted_quantity: number;
  lower_bound: number;
  upper_bound: number;
  confidence: number;
  trimestre: number;
  seasonal_factor: number;
}

export interface PredictionResponse {
  product: {
    id: number;
    name: string;
    reference: string;
    description: string;
    price: number;
    category: string;
  };
  predictions: Prediction[];
  analysis: {
    trend_direction: string;
    trend_percentage: number;
    volatility: number;
    average_confidence: number;
    seasonality_detected: boolean;
    data_quality: string;
  };
  historical_data: {
    last_6_months: Array<{
      Annee: number;
      Mois: number;
      Quantite_Totale: number;
      Nb_Commandes: number;
      Nb_Clients: number;
    }>;
    avg_quantity: number;
    min_quantity: number;
    max_quantity: number;
    avg_orders: number;
    avg_clients: number;
    total_months: number;
  };
}

export interface ModelInfo {
  model_type: string;
  features_count: number;
  features: string[];
  status: string;
  description: string;
}

@Injectable({
  providedIn: 'root'
})
export class MlPredictionService {
  private apiUrl = `${environment.apiUrl}/ml`;

  constructor(private http: HttpClient) {}

  getProducts(): Observable<{ products: Product[]; count: number }> {
    return this.http.get<{ products: Product[]; count: number }>(`${this.apiUrl}/dwh/products?limit=200`);
  }

  predictDemand(productId: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/rami/predict-demand`, { product_id: productId });
  }

  getModelInfo(): Observable<ModelInfo> {
    return this.http.get<ModelInfo>(`${this.apiUrl}/model-info`);
  }
}
