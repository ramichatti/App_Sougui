import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '../core/services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class MlSecurityGuard implements CanActivate {
  
  constructor(
    private router: Router,
    private authService: AuthService
  ) {}

  canActivate(): boolean {
    // Vérifier si l'utilisateur a déjà validé le mot de passe
    const mlAccess = sessionStorage.getItem('ml_access');
    
    if (mlAccess === 'granted') {
      // Vérifier si l'accès n'a pas expiré (30 minutes)
      const expires = sessionStorage.getItem('ml_access_expires');
      if (expires && (Date.now() - parseInt(expires) < 30 * 60 * 1000)) {
        return true;
      } else {
        // Accès expiré
        sessionStorage.removeItem('ml_access');
        sessionStorage.removeItem('ml_access_expires');
      }
    }
    
    // Stocker l'URL demandée pour redirection
    sessionStorage.setItem('ml_return_url', this.router.url);
    
    // Rediriger vers la page de vérification
    this.router.navigate(['/ml-security']);
    return false;
  }
}