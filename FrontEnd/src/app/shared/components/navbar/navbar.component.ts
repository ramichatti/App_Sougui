import { Component, OnInit, OnDestroy, ElementRef, Renderer2, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { TranslationService, Language } from '../../../core/services/translation.service';
import { UserNotificationsService, AppNotification } from '../../../core/services/user-notifications.service';
import { AdminSecurityService } from '../../../core/services/admin-security.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit, OnDestroy {
  menuOpen = false;
  dropdownOpen = false;
  dashboardsDropdownOpen = false;
  mlDropdownOpen = false;
  notifDropdownOpen = false;
  isScrolled = false;
  private hasAnimated = false;
  private lastScrollTop = 0;
  private closeDropdownTimeout: any;
  private closeDashboardsTimeout: any;
  private closeMlTimeout: any;
  private closeNotifTimeout: any;

  constructor(
    public authService: AuthService,
    public translate: TranslationService,
    public notifService: UserNotificationsService,
    private adminSecurity: AdminSecurityService,
    private router: Router,
    private elementRef: ElementRef,
    private renderer: Renderer2
  ) {}

  get notifications() { return this.notifService.notifications; }
  get unreadCount() { return this.notifService.unreadCount; }

  ngOnInit(): void {
    if (!this.hasAnimated) {
      const navElement = this.elementRef.nativeElement.querySelector('.navbar');
      if (navElement) {
        this.renderer.addClass(navElement, 'initial-load');
        this.hasAnimated = true;
        setTimeout(() => this.renderer.removeClass(navElement, 'initial-load'), 300);
      }
    }
    if (this.authService.currentUser()) {
      this.notifService.startPolling();
    }
  }

  ngOnDestroy(): void {
    if (this.closeDropdownTimeout) clearTimeout(this.closeDropdownTimeout);
    if (this.closeDashboardsTimeout) clearTimeout(this.closeDashboardsTimeout);
    if (this.closeMlTimeout) clearTimeout(this.closeMlTimeout);
    if (this.closeNotifTimeout) clearTimeout(this.closeNotifTimeout);
  }

  @HostListener('window:scroll', ['$event'])
  onWindowScroll(): void {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const navElement = this.elementRef.nativeElement.querySelector('.navbar');

    if (scrollTop > 50) {
      if (!this.isScrolled) {
        this.isScrolled = true;
        if (navElement) this.renderer.addClass(navElement, 'scrolled');
      }
    } else {
      if (this.isScrolled) {
        this.isScrolled = false;
        if (navElement) this.renderer.removeClass(navElement, 'scrolled');
      }
    }
    this.lastScrollTop = scrollTop;
  }

  toggleMenu(): void {
    this.menuOpen = !this.menuOpen;
    if (this.menuOpen) this.dropdownOpen = false;
  }

  closeMenu(): void { this.menuOpen = false; }

  toggleDropdown(): void {
    this.dropdownOpen = !this.dropdownOpen;
    if (this.dropdownOpen) this.menuOpen = false;
  }

  openDropdown(): void {
    if (this.closeDropdownTimeout) { clearTimeout(this.closeDropdownTimeout); this.closeDropdownTimeout = null; }
    this.dropdownOpen = true;
    this.menuOpen = false;
  }

  closeDropdown(): void {
    if (this.closeDropdownTimeout) clearTimeout(this.closeDropdownTimeout);
    this.closeDropdownTimeout = setTimeout(() => { this.dropdownOpen = false; }, 200);
  }

  openNotifDropdown(): void {
    if (this.closeNotifTimeout) { clearTimeout(this.closeNotifTimeout); this.closeNotifTimeout = null; }
    this.notifDropdownOpen = true;
  }

  closeNotifDropdown(): void {
    if (this.closeNotifTimeout) clearTimeout(this.closeNotifTimeout);
    this.closeNotifTimeout = setTimeout(() => { this.notifDropdownOpen = false; }, 200);
  }

  toggleNotifDropdown(): void {
    this.notifDropdownOpen = !this.notifDropdownOpen;
  }

  markRead(notif: AppNotification): void {
    this.notifService.markRead(notif);
  }

  markAllRead(): void {
    this.notifService.markAllRead();
  }

  formatNotifTime(dateStr: string): string {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return this.translate.translate('notification.justNow');
    if (diffMins < 60) return `${diffMins} ${this.translate.translate('notification.minutesAgo')}`;
    if (diffHours < 24) return `${diffHours} ${this.translate.translate('notification.hoursAgo')}`;
    return `${diffDays} ${this.translate.translate('notification.daysAgo')}`;
  }

  logout(): void {
    this.closeDropdown();
    this.notifService.stopPolling();
    this.adminSecurity.clear();
    this.authService.logout();
  }

  getRoleLabel(role: string | null): string {
    if (!role) return 'Aucun rôle';
    // Return the role name directly without translation
    return role;
  }

  hasProfileImage(): boolean {
    return !!(this.authService.currentUser()?.profile_image);
  }

  getProfileImage(): string {
    const img = this.authService.currentUser()?.profile_image;
    if (!img) return '';
    return img.startsWith('data:image') ? img : 'data:image/jpeg;base64,' + img;
  }

  getUserInitials(): string {
    const user = this.authService.currentUser();
    return ((user?.first_name?.[0] || '') + (user?.last_name?.[0] || '')).toUpperCase() || '?';
  }

  changeLanguage(lang: Language): void {
    this.translate.setLanguage(lang);
    this.closeDropdown();
  }

  openDashboardsDropdown(): void {
    if (this.closeDashboardsTimeout) { clearTimeout(this.closeDashboardsTimeout); this.closeDashboardsTimeout = null; }
    this.dashboardsDropdownOpen = true;
    this.dropdownOpen = false;
    this.menuOpen = false;
  }

  closeDashboardsDropdown(): void {
    if (this.closeDashboardsTimeout) clearTimeout(this.closeDashboardsTimeout);
    this.closeDashboardsTimeout = setTimeout(() => { this.dashboardsDropdownOpen = false; }, 200);
  }

  isDashboardRoute(): boolean {
    return this.router.url.includes('/dashboard');
  }

  openMlDropdown(): void {
    if (this.closeMlTimeout) { clearTimeout(this.closeMlTimeout); this.closeMlTimeout = null; }
    this.mlDropdownOpen = true;
    this.dropdownOpen = false;
    this.menuOpen = false;
  }

  closeMlDropdown(): void {
    if (this.closeMlTimeout) clearTimeout(this.closeMlTimeout);
    this.closeMlTimeout = setTimeout(() => { this.mlDropdownOpen = false; }, 200);
  }

  isMLRoute(): boolean {
    const url = this.router.url;
    return url.includes('/admin/ml-models') ||
           url.includes('/predict-cost') ||
           url.includes('/distance-analysis') ||
           url.includes('/demand-prediction') ||
           url.includes('/best-seller-b2c') ||
           url.includes('/client-segmentation');
  }
}
