import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Reclamation {
  id: number;
  user_id: number;
  user_name: string;
  user_email: string;
  user_image?: string;
  title: string;
  description: string;
  category: 'technique' | 'commercial' | 'produit' | 'service' | 'autre';
  priority: 'basse' | 'moyenne' | 'haute' | 'urgente';
  status: 'nouvelle' | 'en_cours' | 'resolue' | 'fermee';
  response?: string;
  has_attachment?: boolean;
  attachment_name?: string;
  attachment_type?: string;
  attachment_data?: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
  admin_notified?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class ReclamationService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getReclamations(): Observable<{ reclamations: Reclamation[] }> {
    return this.http.get<{ reclamations: Reclamation[] }>(`${this.apiUrl}/reclamations/`);
  }

  createReclamation(data: Partial<Reclamation>): Observable<any> {
    return this.http.post(`${this.apiUrl}/reclamations/`, data);
  }

  updateReclamation(id: number, data: Partial<Reclamation>): Observable<any> {
    return this.http.put(`${this.apiUrl}/reclamations/${id}`, data);
  }

  deleteReclamation(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/reclamations/${id}`);
  }

  getStats(): Observable<any> {
    return this.http.get(`${this.apiUrl}/reclamations/stats`);
  }

  getUnreadCount(): Observable<{ count: number }> {
    return this.http.get<{ count: number }>(`${this.apiUrl}/reclamations/unread-count`);
  }

  markNotified(ids?: number[]): Observable<any> {
    return this.http.post(`${this.apiUrl}/reclamations/mark-notified`, { ids });
  }

  getAttachment(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/reclamations/${id}/attachment`);
  }
}
