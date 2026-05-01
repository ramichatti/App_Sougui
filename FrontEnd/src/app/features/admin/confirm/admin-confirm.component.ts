import { Component, signal, ViewChild, ElementRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AdminSecurityService } from '../../../core/services/admin-security.service';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-admin-confirm',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-confirm.component.html',
  styleUrls: ['./admin-confirm.component.css']
})
export class AdminConfirmComponent implements OnInit {
  @ViewChild('passwordInput') passwordInput!: ElementRef;

  password = '';
  showPassword = false;
  isLoading = signal(false);
  errorMsg = signal('');
  returnUrl = '/admin/users';
  attempts = signal(0);

  constructor(
    private security: AdminSecurityService,
    public auth: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.returnUrl = this.route.snapshot.queryParamMap.get('return') ?? '/admin/users';

    // Already verified — go straight through
    if (this.security.isVerified()) {
      this.router.navigateByUrl(this.returnUrl);
    }

    setTimeout(() => this.passwordInput?.nativeElement?.focus(), 200);
  }

  submit(): void {
    if (!this.password.trim() || this.isLoading()) return;

    this.isLoading.set(true);
    this.errorMsg.set('');

    this.security.verify(this.password).subscribe(valid => {
      this.isLoading.set(false);
      if (valid) {
        this.router.navigateByUrl(this.returnUrl);
      } else {
        this.attempts.update(n => n + 1);
        this.errorMsg.set('Mot de passe incorrect. Veuillez réessayer.');
        this.password = '';
        setTimeout(() => this.passwordInput?.nativeElement?.focus(), 100);
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/home']);
  }

  onKeydown(e: KeyboardEvent): void {
    if (e.key === 'Enter') this.submit();
  }

  get user() { return this.auth.currentUser(); }

  getUserInitials(): string {
    const u = this.user;
    return ((u?.first_name?.[0] ?? '') + (u?.last_name?.[0] ?? '')).toUpperCase() || 'A';
  }

  hasProfileImage(): boolean {
    return !!(this.user?.profile_image);
  }

  getProfileImage(): string {
    const img = this.user?.profile_image;
    if (!img) return '';
    return img.startsWith('data:image') ? img : 'data:image/jpeg;base64,' + img;
  }

  getPageLabel(url: string): string {
    if (url.includes('users')) return 'Gestion des Utilisateurs';
    if (url.includes('roles')) return 'Gestion des Rôles & Accès';
    if (url.includes('powerbi')) return 'Gestion des Dashboards Power BI';
    return 'Administration';
  }

  getPageIcon(url: string): string {
    if (url.includes('users')) return 'users';
    if (url.includes('roles')) return 'shield';
    if (url.includes('powerbi')) return 'chart';
    return 'lock';
  }
}
