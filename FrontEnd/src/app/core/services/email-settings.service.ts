import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface EmailSettings {
  mail_server: string;
  mail_port: number;
  mail_use_tls: boolean;
  mail_username: string;
  mail_password: string;
  is_configured: boolean;
  last_updated: string | null;
  updated_by: string | null;
}

export interface TestEmailRequest {
  mail_server: string;
  mail_port: number;
  mail_use_tls: boolean;
  mail_username: string;
  mail_password: string;
  test_recipient?: string;
}

export interface TestEmailResponse {
  success: boolean;
  message?: string;
  error?: string;
  details?: {
    server: string;
    port: number;
    username: string;
    tls: boolean;
  };
}

@Injectable({
  providedIn: 'root'
})
export class EmailSettingsService {
  private apiUrl = `${environment.apiUrl}/email-settings`;

  constructor(private http: HttpClient) {}

  getSettings(): Observable<EmailSettings> {
    return this.http.get<EmailSettings>(this.apiUrl);
  }

  updateSettings(settings: Partial<EmailSettings>): Observable<any> {
    return this.http.put(this.apiUrl, settings);
  }

  testConnection(request: TestEmailRequest): Observable<TestEmailResponse> {
    return this.http.post<TestEmailResponse>(`${this.apiUrl}/test`, request);
  }

  getHistory(): Observable<any> {
    return this.http.get(`${this.apiUrl}/history`);
  }
}
