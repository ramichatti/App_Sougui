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

  constructor(
    public authService: AuthService,
    private dashboardService: DashboardService,
    private router: Router,
    private route: ActivatedRoute,
    private sanitizer: DomSanitizer,
    public translationService: TranslationService
  ) {}

  ngOnInit(): void {
    // Check if a specific dashboard ID is provided in the route
    this.route.params.subscribe(params => {
      if (params['id']) {
        this.specificDashboardId.set(+params['id']);
      }
      this.loadDashboards();
    });
  }

  loadDashboards(): void {
    this.isLoading.set(true);
    this.dashboardService.getMyDashboards().subscribe({
      next: (response) => {
        this.dashboards.set(response.dashboards);
        
        // If a specific dashboard ID is provided, find and display it
        const specificId = this.specificDashboardId();
        if (specificId) {
          const index = response.dashboards.findIndex(d => d.id === specificId);
          if (index !== -1) {
            this.currentDashboardIndex.set(index);
          }
        }
        
        this.isLoading.set(false);
      },
      error: (error) => {
        this.errorMessage.set(this.translationService.translate('dashboard.error'));
        this.isLoading.set(false);
      }
    });
  }

  getSafeUrl(url: string): SafeResourceUrl {
    return this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }

  logout(): void {
    this.authService.logout();
  }

  goToAdmin(): void {
    this.router.navigate(['/admin']);
  }

  getRoleLabel(role: string): string {
    return this.translationService.translate(`role.${role}`);
  }

  selectDashboard(index: number): void {
    this.currentDashboardIndex.set(index);
  }

  getCurrentDashboard(): Dashboard | null {
    const dashboards = this.dashboards();
    const index = this.currentDashboardIndex();
    return dashboards.length > 0 && index < dashboards.length ? dashboards[index] : null;
  }

  nextDashboard(): void {
    const dashboards = this.dashboards();
    if (this.currentDashboardIndex() < dashboards.length - 1) {
      this.currentDashboardIndex.set(this.currentDashboardIndex() + 1);
    }
  }

  previousDashboard(): void {
    if (this.currentDashboardIndex() > 0) {
      this.currentDashboardIndex.set(this.currentDashboardIndex() - 1);
    }
  }
}
