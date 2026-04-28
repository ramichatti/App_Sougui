import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.css']
})
export class ForgotPasswordComponent {
  step = signal<'email' | 'code' | 'password'>('email');
  email = '';
  code = '';
  newPassword = '';
  confirmPassword = '';
  message = signal<string>('');
  errorMessage = signal<string>('');
  isLoading = signal<boolean>(false);
  
  // Track if email was successfully sent
  private emailSent = false;
  // Track if code was verified
  private codeVerified = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmitEmail(): void {
    if (!this.email) {
      this.errorMessage.set('Veuillez entrer votre email');
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.email)) {
      this.errorMessage.set('Format d\'email invalide');
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set('');
    this.message.set('');

    this.authService.forgotPassword({ email: this.email }).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        this.emailSent = true;

        let successMsg = response.message || `Code envoyé à ${this.email}. Vérifiez votre boîte de réception (expire dans 15 minutes).`;
        if (response.debug_code) {
          successMsg += ` — Code: ${response.debug_code}`;
        }

        this.message.set(successMsg);
        this.step.set('code');
      },
      error: (error) => {
        this.isLoading.set(false);
        this.emailSent = false;
        const errorMsg = error.error?.error || error.error?.message || 'Erreur lors de l\'envoi du code';
        this.errorMessage.set(errorMsg);
      }
    });
  }

  onSubmitCode(): void {
    // Check if email was sent first
    if (!this.emailSent) {
      this.errorMessage.set('Veuillez d\'abord demander un code par email');
      this.step.set('email');
      return;
    }

    if (!this.code) {
      this.errorMessage.set('Veuillez entrer le code');
      return;
    }

    if (this.code.length !== 6) {
      this.errorMessage.set('Le code doit contenir exactement 6 chiffres');
      return;
    }

    // Validate code is numeric
    if (!/^\d{6}$/.test(this.code)) {
      this.errorMessage.set('Le code doit contenir uniquement des chiffres');
      return;
    }

    // Verify code with backend
    this.isLoading.set(true);
    this.errorMessage.set('');
    this.message.set('');

    this.authService.verifyResetCode({
      email: this.email,
      code: this.code
    }).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        this.codeVerified = true;
        this.message.set('✅ Code vérifié ! Créez votre nouveau mot de passe');
        this.step.set('password');
      },
      error: (error) => {
        this.isLoading.set(false);
        this.codeVerified = false;
        const errorMsg = error.error?.error || error.error?.message || 'Code invalide ou expiré';
        this.errorMessage.set(errorMsg);
      }
    });
  }

  onSubmitPassword(): void {
    // Check if code was verified
    if (!this.codeVerified) {
      this.errorMessage.set('Veuillez d\'abord vérifier le code');
      this.step.set('code');
      return;
    }

    if (!this.newPassword || !this.confirmPassword) {
      this.errorMessage.set('Veuillez remplir tous les champs');
      return;
    }

    if (this.newPassword.length < 6) {
      this.errorMessage.set('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }

    if (this.newPassword !== this.confirmPassword) {
      this.errorMessage.set('Les mots de passe ne correspondent pas');
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set('');
    this.message.set('');

    this.authService.resetPassword({
      email: this.email,
      code: this.code,
      new_password: this.newPassword
    }).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        this.message.set('✅ Mot de passe réinitialisé avec succès ! Redirection...');
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 2000);
      },
      error: (error) => {
        this.isLoading.set(false);
        const errorMsg = error.error?.error || error.error?.message || 'Erreur lors de la réinitialisation';
        this.errorMessage.set(errorMsg);
      }
    });
  }
}
