import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { TranslationService } from '../../../core/services/translation.service';
import { ToastService } from '../../../core/services/toast.service';
import { ToastComponent } from '../../../shared/components/toast/toast.component';

type ErrorType = 'blocked' | 'not_found' | 'wrong_password' | 'field' | 'network' | null;

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, ToastComponent],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  email = '';
  password = '';
  errorMessage = signal<string>('');
  errorType = signal<ErrorType>(null);
  isLoading = signal<boolean>(false);
  showPassword = signal<boolean>(false);
  shaking = signal<boolean>(false);

  constructor(
    private authService: AuthService,
    public translate: TranslationService,
    private router: Router,
    private toastService: ToastService
  ) {}

  togglePassword(): void {
    this.showPassword.update(v => !v);
  }

  clearError(): void {
    this.errorType.set(null);
    this.errorMessage.set('');
  }

  onSubmit(): void {
    this.clearError();

    if (!this.email || !this.email.trim()) {
      this.errorType.set('field');
      this.errorMessage.set(this.translate.translate('login.error.emailRequired'));
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.email)) {
      this.errorType.set('field');
      this.errorMessage.set(this.translate.translate('login.error.emailInvalid'));
      return;
    }

    if (!this.password || !this.password.trim()) {
      this.errorType.set('field');
      this.errorMessage.set(this.translate.translate('login.error.passwordRequired'));
      return;
    }

    if (this.password.length < 6) {
      this.errorType.set('field');
      this.errorMessage.set(this.translate.translate('login.error.passwordTooShort'));
      return;
    }

    this.isLoading.set(true);

    this.authService.login({ email: this.email, password: this.password }).subscribe({
      next: () => {
        this.isLoading.set(false);
        this.router.navigate(['/home']);
      },
      error: (error) => {
        this.isLoading.set(false);
        const status: number = error.status;
        const serverMsg: string = error.error?.error || '';

        if (status === 403 || serverMsg.toLowerCase().includes('bloqué') || serverMsg.toLowerCase().includes('blocked')) {
          this.errorType.set('blocked');
          this.toastService.error(
            this.translate.translate('toast.login.blocked.title'),
            this.translate.translate('toast.login.blocked.message')
          );
        } else if (serverMsg.toLowerCase().includes('aucun compte') || serverMsg.toLowerCase().includes('not found') || serverMsg.toLowerCase().includes('no account')) {
          this.errorType.set('not_found');
          this.toastService.error(
            this.translate.translate('toast.login.notFound.title'),
            this.translate.translate('toast.login.notFound.message')
          );
        } else if (serverMsg.toLowerCase().includes('incorrect') || serverMsg.toLowerCase().includes('mot de passe') || serverMsg.toLowerCase().includes('wrong') || serverMsg.toLowerCase().includes('password')) {
          this.errorType.set('wrong_password');
          this.toastService.error(
            this.translate.translate('toast.login.wrongPassword.title'),
            this.translate.translate('toast.login.wrongPassword.message')
          );
        } else {
          this.errorType.set('network');
          this.toastService.error(
            this.translate.translate('toast.login.error.title'),
            serverMsg || this.translate.translate('toast.login.error.message')
          );
        }

        this.errorMessage.set(serverMsg || this.translate.translate('login.error.connection'));
        this.triggerShake();
      }
    });
  }

  private triggerShake(): void {
    this.shaking.set(true);
    setTimeout(() => this.shaking.set(false), 600);
  }
}
