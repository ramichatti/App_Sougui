import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { TranslationService } from '../../core/services/translation.service';

@Component({
  selector: 'app-ml-security',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './ml-security.component.html',
  styleUrls: ['./ml-security.component.css']
})
export class MlSecurityComponent {
  password: string = '';
  errorMessage: string = '';
  isLoading: boolean = false;

  constructor(
    private router: Router,
    private authService: AuthService,
    public translate: TranslationService
  ) {}

  getUserInitials(): string {
    const user = this.authService.currentUser();
    return ((user?.first_name?.[0] || '') + (user?.last_name?.[0] || '')).toUpperCase() || 'A';
  }

  getUserName(): string {
    const user = this.authService.currentUser();
    return `${user?.first_name || ''} ${user?.last_name || ''}`.trim() || this.translate.translate('role.admin');
  }

  verifyPassword() {
    if (!this.password) {
      this.errorMessage = this.translate.translate('profile.passwordRequired');
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.authService.verifyPassword(this.password).subscribe({
      next: (response: any) => {
        if (response.valid === true) {
          sessionStorage.setItem('ml_access', 'granted');
          sessionStorage.setItem('ml_access_expires', Date.now().toString());
          
          const returnUrl = sessionStorage.getItem('ml_return_url') || '/admin/ml-models';
          sessionStorage.removeItem('ml_return_url');
          this.router.navigate([returnUrl]);
        } else {
          this.errorMessage = this.translate.translate('mlSecurity.incorrectPassword');
        }
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = this.translate.translate('common.connectionError');
        this.isLoading = false;
      }
    });
  }

  goBack() {
    this.router.navigate(['/home']);
  }
}