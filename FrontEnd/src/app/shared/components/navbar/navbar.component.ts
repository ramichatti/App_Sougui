import { Component, OnInit, OnDestroy, ElementRef, Renderer2, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { TranslationService, Language } from '../../../core/services/translation.service';

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
  isScrolled = false;
  private hasAnimated = false;
  private lastScrollTop = 0;
  private closeDropdownTimeout: any;
  private closeDashboardsTimeout: any;

  constructor(
    public authService: AuthService,
    public translate: TranslationService,
    private router: Router,
    private elementRef: ElementRef,
    private renderer: Renderer2
  ) {}

  ngOnInit(): void {
    if (!this.hasAnimated) {
      const navElement = this.elementRef.nativeElement.querySelector('.navbar');
      if (navElement) {
        this.renderer.addClass(navElement, 'initial-load');
        this.hasAnimated = true;
        setTimeout(() => this.renderer.removeClass(navElement, 'initial-load'), 300);
      }
    }
  }

  ngOnDestroy(): void {
    if (this.closeDropdownTimeout) {
      clearTimeout(this.closeDropdownTimeout);
    }
    if (this.closeDashboardsTimeout) {
      clearTimeout(this.closeDashboardsTimeout);
    }
  }

  @HostListener('window:scroll', ['$event'])
  onWindowScroll(): void {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const navElement = this.elementRef.nativeElement.querySelector('.navbar');
    
    if (scrollTop > 50) {
      if (!this.isScrolled) {
        this.isScrolled = true;
        if (navElement) {
          this.renderer.addClass(navElement, 'scrolled');
        }
      }
    } else {
      if (this.isScrolled) {
        this.isScrolled = false;
        if (navElement) {
          this.renderer.removeClass(navElement, 'scrolled');
        }
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
    if (this.closeDropdownTimeout) {
      clearTimeout(this.closeDropdownTimeout);
      this.closeDropdownTimeout = null;
    }
    this.dropdownOpen = true; 
    this.menuOpen = false;
  }

  closeDropdown(): void { 
    // Add a small delay to prevent accidental closing
    if (this.closeDropdownTimeout) {
      clearTimeout(this.closeDropdownTimeout);
    }
    this.closeDropdownTimeout = setTimeout(() => {
      this.dropdownOpen = false;
    }, 200);
  }

  logout(): void {
    this.closeDropdown();
    this.authService.logout();
  }

  getRoleLabel(role: string | null): string {
    if (!role) return '';
    return this.translate.translate(`role.${role}`) || role;
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
    if (this.closeDashboardsTimeout) {
      clearTimeout(this.closeDashboardsTimeout);
      this.closeDashboardsTimeout = null;
    }
    this.dashboardsDropdownOpen = true;
    this.dropdownOpen = false;
    this.menuOpen = false;
  }

  closeDashboardsDropdown(): void {
    if (this.closeDashboardsTimeout) {
      clearTimeout(this.closeDashboardsTimeout);
    }
    this.closeDashboardsTimeout = setTimeout(() => {
      this.dashboardsDropdownOpen = false;
    }, 200);
  }

  isDashboardRoute(): boolean {
    return this.router.url.includes('/dashboard');
  }
}
