import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { TranslationService } from '../../core/services/translation.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  currentYear = new Date().getFullYear();
  
  // Animated counters
  productsCount = signal(0);
  artisansCount = signal(0);
  clientsCount = signal(0);

  constructor(
    public authService: AuthService,
    public translationService: TranslationService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Animate counters on page load
    this.animateCounter(this.productsCount, 500, 2000);
    this.animateCounter(this.artisansCount, 50, 2000);
    this.animateCounter(this.clientsCount, 1000, 2000);
  }

  animateCounter(signal: any, target: number, duration: number): void {
    const start = 0;
    const increment = target / (duration / 16); // 60fps
    let current = start;

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        signal.set(target);
        clearInterval(timer);
      } else {
        signal.set(Math.floor(current));
      }
    }, 16);
  }

  navigateTo(route: string): void {
    this.router.navigate([route]);
  }

  scrollToFeatures(): void {
    const element = document.querySelector('.app-purpose-section');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  getRoleLabel(role: string | null): string {
    if (!role) return '';
    return this.translationService.translate(`role.${role}`);
  }

  getRoleTitle(role: string | null): string {
    if (!role) return '';
    return this.translationService.translate(`home.role.${role}.title`);
  }

  getRoleDescription(role: string | null): string {
    if (!role) return '';
    return this.translationService.translate(`home.role.${role}.description`);
  }

  getBIDescription(role: string | null): string {
    if (!role) return '';
    return this.translationService.translate(`home.role.${role}.bi.description`);
  }

  getMLDescription(role: string | null): string {
    if (!role) return '';
    return this.translationService.translate(`home.role.${role}.ml.description`);
  }

  getBIFeatures(role: string | null): string[] {
    if (!role) return [];
    const features: string[] = [];
    for (let i = 1; i <= 4; i++) {
      const key = `home.role.${role}.bi.feature${i}`;
      const translation = this.translationService.translate(key);
      if (translation !== key) features.push(translation);
    }
    return features;
  }

  getMLFeatures(role: string | null): string[] {
    if (!role) return [];
    const features: string[] = [];
    for (let i = 1; i <= 4; i++) {
      const key = `home.role.${role}.ml.feature${i}`;
      const translation = this.translationService.translate(key);
      if (translation !== key) features.push(translation);
    }
    return features;
  }
}
