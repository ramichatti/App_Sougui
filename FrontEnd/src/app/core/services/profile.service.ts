import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { User } from '../models/user.model';

@Injectable({
  providedIn: 'root'
})
export class ProfileService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getProfile(): Observable<{ user: User }> {
    return this.http.get<{ user: User }>(`${this.apiUrl}/profile/`);
  }

  updateProfile(data: Partial<User>): Observable<any> {
    return this.http.put(`${this.apiUrl}/profile/`, data);
  }

  uploadImage(imageData: string): Observable<any> {
    // Extract base64 data without data URI prefix
    let base64Data = imageData;
    if (imageData.includes(',')) {
      base64Data = imageData.split(',')[1];
    }
    return this.http.put(`${this.apiUrl}/profile/photo`, { profile_image: base64Data });
  }

  changePassword(data: { current_password: string; new_password: string }): Observable<any> {
    return this.http.put(`${this.apiUrl}/profile/password`, data);
  }

  requestPasswordChange(): Observable<any> {
    return this.http.post(`${this.apiUrl}/profile/request-password-change`, {});
  }

  verifyPasswordChangeCode(code: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/profile/verify-password-change-code`, { code });
  }

  changePasswordWithCode(data: { code: string; current_password: string; new_password: string }): Observable<any> {
    return this.http.post(`${this.apiUrl}/profile/change-password-with-code`, data);
  }
}
