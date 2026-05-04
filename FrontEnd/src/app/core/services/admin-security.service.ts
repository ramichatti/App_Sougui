import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map, catchError, of } from 'rxjs';
import { environment } from '../../../environments/environment';

const SESSION_KEY = 'admin_verified_at';
const TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes

@Injectable({ providedIn: 'root' })
export class AdminSecurityService {
  private apiUrl = environment.apiUrl;

  isVerified = signal<boolean>(this.checkSession());

  constructor(private http: HttpClient) {}

  private checkSession(): boolean {
    const ts = sessionStorage.getItem(SESSION_KEY);
    if (!ts) return false;
    return Date.now() - parseInt(ts, 10) < TIMEOUT_MS;
  }

  verify(password: string): Observable<boolean> {
    return this.http.post<{ valid: boolean }>(
      `${this.apiUrl}/auth/verify-password`,
      { password }
    ).pipe(
      map(res => {
        if (res.valid) {
          sessionStorage.setItem(SESSION_KEY, Date.now().toString());
          this.isVerified.set(true);
        }
        return res.valid;
      }),
      catchError(() => of(false))
    );
  }

  /** Call when admin logs out so session is cleared */
  clear(): void {
    sessionStorage.removeItem(SESSION_KEY);
    this.isVerified.set(false);
  }
}
