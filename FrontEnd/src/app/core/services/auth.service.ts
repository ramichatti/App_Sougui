import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { User, LoginRequest, LoginResponse, ForgotPasswordRequest, VerifyCodeRequest, ResetPasswordRequest } from '../models/user.model';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  currentUser = signal<User | null>(null);
  isAuthenticated = signal<boolean>(false);

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    this.loadUserFromStorage();
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/auth/login`, credentials).pipe(
      tap(response => {
        this.setSession(response);
      })
    );
  }

  forgotPassword(data: ForgotPasswordRequest): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/forgot-password`, data);
  }

  verifyResetCode(data: VerifyCodeRequest): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/verify-reset-code`, data);
  }

  resetPassword(data: ResetPasswordRequest): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/reset-password`, data);
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    this.currentUser.set(null);
    this.isAuthenticated.set(false);
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  // ============================================
  // NOUVELLE MÉTHODE : VÉRIFICATION MOT DE PASSE
  // ============================================
  verifyPassword(password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/verify-password`, { password });
  }

  private setSession(authResult: LoginResponse): void {
    localStorage.setItem('access_token', authResult.access_token);
    localStorage.setItem('user', JSON.stringify(authResult.user));
    this.currentUser.set(authResult.user);
    this.isAuthenticated.set(true);
  }

  private loadUserFromStorage(): void {
    const token = this.getToken();
    const userStr = localStorage.getItem('user');
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        this.currentUser.set(user);
        this.isAuthenticated.set(true);
      } catch (e) {
        this.logout();
      }
    }
  }

  isAdmin(): boolean {
    return this.currentUser()?.is_admin === true;
  }

  refreshUser(): void {
    this.http.get<{ user: User }>(`${this.apiUrl}/auth/me`).subscribe({
      next: (response) => {
        const user = response.user;
        this.currentUser.set(user);
        localStorage.setItem('user', JSON.stringify(user));
      },
      error: () => {}
    });
  }
}