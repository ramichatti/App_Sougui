import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface PowerBIDashboard {
  id: number;
  dashboard_name: string;
  embed_url: string;
  description?: string;
  is_active: boolean;
  created_at?: string;
}

@Injectable({
  providedIn: 'root'
})
export class PowerBIService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getDashboards(): Observable<{ dashboards: PowerBIDashboard[] }> {
    return this.http.get<{ dashboards: PowerBIDashboard[] }>(`${this.apiUrl}/powerbi/dashboards`);
  }

  getAllDashboards(): Observable<{ dashboards: PowerBIDashboard[] }> {
    return this.http.get<{ dashboards: PowerBIDashboard[] }>(`${this.apiUrl}/powerbi/dashboards/all`);
  }

  createDashboard(data: Partial<PowerBIDashboard>): Observable<any> {
    return this.http.post(`${this.apiUrl}/powerbi/dashboards`, data);
  }

  updateDashboard(id: number, data: Partial<PowerBIDashboard>): Observable<any> {
    return this.http.put(`${this.apiUrl}/powerbi/dashboards/${id}`, data);
  }

  deleteDashboard(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/powerbi/dashboards/${id}`);
  }
}
