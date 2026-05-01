import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { DashboardService } from '../../core/services/dashboard.service';
import { Dashboard } from '../../core/models/dashboard.model';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { TranslationService } from '../../core/services/translation.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  dashboards = signal<Dashboard[]>([]);
  isLoading = signal<boolean>(true);
  errorMessage = signal<string>('');
  currentDashboardIndex = signal<number>(0);
  specificDashboardId = signal<number | null>(null);
  showIframe = signal<boolean>(true);

  constructor(
    public authService: AuthService,
    private dashboardService: DashboardService,
    private router: Router,
    private route: ActivatedRoute,
    private sanitizer: DomSanitizer,
    public translationService: TranslationService
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      if (params['id']) {
        this.specificDashboardId.set(+params['id']);
      }
      this.loadDashboards();
    });
  }

  loadDashboards(): void {
    this.isLoading.set(true);
    this.errorMessage.set('');
    this.dashboardService.getMyDashboards().subscribe({
      next: (response) => {
        this.dashboards.set(response.dashboards);

        const specificId = this.specificDashboardId();
        if (specificId) {
          const index = response.dashboards.findIndex(d => d.id === specificId);
          if (index !== -1) {
            this.currentDashboardIndex.set(index);
          }
        }

        this.showIframe.set(true);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set(this.translationService.translate('dashboard.error'));
        this.isLoading.set(false);
      }
    });
  }

  // Only called by the refresh button — never automatically
  refreshDashboard(): void {
    this.showIframe.set(false);
    setTimeout(() => this.showIframe.set(true), 80);
  }

  getSafeUrl(url: string): SafeResourceUrl {
    return this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }

  getCurrentDashboard(): Dashboard | null {
    const list = this.dashboards();
    const i = this.currentDashboardIndex();
    return list.length > 0 && i < list.length ? list[i] : null;
  }

  logout(): void { this.authService.logout(); }
  goToAdmin(): void { this.router.navigate(['/admin']); }
}
