import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Dashboard, DashboardResponse } from '../models/dashboard.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getMyDashboards(): Observable<DashboardResponse> {
    return this.http.get<DashboardResponse>(`${this.apiUrl}/dashboard/my-dashboards`);
  }

  getAllDashboards(): Observable<{ dashboards: Dashboard[] }> {
    return this.http.get<{ dashboards: Dashboard[] }>(`${this.apiUrl}/admin/dashboards`);
  }

  createDashboard(dashboard: Partial<Dashboard>): Observable<any> {
    return this.http.post(`${this.apiUrl}/admin/dashboards`, dashboard);
  }

  updateDashboard(id: number, dashboard: Partial<Dashboard>): Observable<any> {
    return this.http.put(`${this.apiUrl}/admin/dashboards/${id}`, dashboard);
  }

  deleteDashboard(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/admin/dashboards/${id}`);
  }
}
