import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { TranslationService } from '../../../core/services/translation.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  email = '';
  password = '';
  errorMessage = signal<string>('');
  isLoading = signal<boolean>(false);

  constructor(
    private authService: AuthService,
    public translate: TranslationService,
    private router: Router
  ) {}

  onSubmit(): void {
    // Validate email
    if (!this.email || !this.email.trim()) {
      this.errorMessage.set(this.translate.translate('login.error.emailRequired'));
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.email)) {
      this.errorMessage.set(this.translate.translate('login.error.emailInvalid'));
      return;
    }

    // Validate password
    if (!this.password || !this.password.trim()) {
      this.errorMessage.set(this.translate.translate('login.error.passwordRequired'));
      return;
    }

    if (this.password.length < 6) {
      this.errorMessage.set(this.translate.translate('login.error.passwordTooShort'));
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set('');

    this.authService.login({ email: this.email, password: this.password }).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        // Redirect to home page after successful login
        this.router.navigate(['/home']);
      },
      error: (error) => {
        this.isLoading.set(false);
        this.errorMessage.set(error.error?.message || this.translate.translate('login.error.connection'));
      }
    });
  }
}
