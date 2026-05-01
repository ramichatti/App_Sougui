import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { TranslationService } from '../../../core/services/translation.service';
import { ToastService } from '../../../core/services/toast.service';
import { ToastComponent } from '../../../shared/components/toast/toast.component';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, ToastComponent],
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
  showNewPassword = signal<boolean>(false);
  showConfirmPassword = signal<boolean>(false);
  
  // Track if email was successfully sent
  private emailSent = false;
  // Track if code was verified
  private codeVerified = false;

  constructor(
    private authService: AuthService,
    public translate: TranslationService,
    private router: Router,
    private toastService: ToastService
  ) {}

  toggleNewPassword(): void {
    this.showNewPassword.update(v => !v);
  }

  toggleConfirmPassword(): void {
    this.showConfirmPassword.update(v => !v);
  }

  onSubmitEmail(): void {
    if (!this.email) {
      this.errorMessage.set(this.translate.translate('forgot.error.emailRequired'));
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.email)) {
      this.errorMessage.set(this.translate.translate('forgot.error.emailInvalid'));
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set('');
    this.message.set('');

    this.authService.forgotPassword({ email: this.email }).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        this.emailSent = true;

        let successMsg = response.message || this.translate.translate('forgot.success.codeSent').replace('{email}', this.email);
        if (response.debug_code) {
          successMsg += ` — Code: ${response.debug_code}`;
        }

        this.message.set(successMsg);
        this.toastService.success(
          this.translate.translate('toast.forgot.codeSent.title'),
          this.translate.translate('toast.forgot.codeSent.message')
        );
        this.step.set('code');
      },
      error: (error) => {
        this.isLoading.set(false);
        this.emailSent = false;
        const errorMsg = error.error?.error || error.error?.message || this.translate.translate('forgot.error.sendCode');
        this.errorMessage.set(errorMsg);
        this.toastService.error(
          this.translate.translate('toast.forgot.error.title'),
          errorMsg
        );
      }
    });
  }

  onSubmitCode(): void {
    // Check if email was sent first
    if (!this.emailSent) {
      this.errorMessage.set(this.translate.translate('forgot.error.emailFirst'));
      this.step.set('email');
      return;
    }

    if (!this.code) {
      this.errorMessage.set(this.translate.translate('forgot.error.codeRequired'));
      return;
    }

    if (this.code.length !== 6) {
      this.errorMessage.set(this.translate.translate('forgot.error.codeLength'));
      return;
    }

    // Validate code is numeric
    if (!/^\d{6}$/.test(this.code)) {
      this.errorMessage.set(this.translate.translate('forgot.error.codeNumeric'));
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
        this.message.set(this.translate.translate('forgot.success.codeVerified'));
        this.toastService.success(
          this.translate.translate('toast.forgot.codeVerified.title'),
          this.translate.translate('toast.forgot.codeVerified.message')
        );
        this.step.set('password');
      },
      error: (error) => {
        this.isLoading.set(false);
        this.codeVerified = false;
        const errorMsg = error.error?.error || error.error?.message || this.translate.translate('forgot.error.invalidCode');
        this.errorMessage.set(errorMsg);
        this.toastService.error(
          this.translate.translate('toast.forgot.error.title'),
          errorMsg
        );
      }
    });
  }

  onSubmitPassword(): void {
    // Check if code was verified
    if (!this.codeVerified) {
      this.errorMessage.set(this.translate.translate('forgot.error.verifyFirst'));
      this.step.set('code');
      return;
    }

    if (!this.newPassword || !this.confirmPassword) {
      this.errorMessage.set(this.translate.translate('forgot.error.passwordRequired'));
      return;
    }

    if (this.newPassword.length < 6) {
      this.errorMessage.set(this.translate.translate('forgot.error.passwordTooShort'));
      return;
    }

    if (this.newPassword !== this.confirmPassword) {
      this.errorMessage.set(this.translate.translate('forgot.error.passwordMismatch'));
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
        this.message.set(this.translate.translate('forgot.success.passwordReset'));
        this.toastService.success(
          this.translate.translate('toast.forgot.passwordReset.title'),
          this.translate.translate('toast.forgot.passwordReset.message')
        );
        setTimeout(() => {
          this.router.navigate(['/login']);
        }, 2000);
      },
      error: (error) => {
        this.isLoading.set(false);
        const errorMsg = error.error?.error || error.error?.message || this.translate.translate('forgot.error.resetFailed');
        this.errorMessage.set(errorMsg);
        this.toastService.error(
          this.translate.translate('toast.forgot.error.title'),
          errorMsg
        );
      }
    });
  }
}
