import { Component, OnInit, signal, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { DashboardService } from '../../core/services/dashboard.service';
import { Dashboard } from '../../core/models/dashboard.model';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { TranslationService } from '../../core/services/translation.service';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

interface DashboardUser {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  role: string;
  is_admin: boolean;
  profile_image: string | null;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DashboardComponent implements OnInit {
  dashboards = signal<Dashboard[]>([]);
  isLoading = signal<boolean>(true);
  errorMessage = signal<string>('');
  currentDashboardIndex = signal<number>(0);
  specificDashboardId = signal<number | null>(null);
  iframeKey = signal<number>(0); // Used to force iframe reload
  dashboardUsers = signal<DashboardUser[]>([]);
  isLoadingUsers = signal<boolean>(false);
  showUsersPanel = signal<boolean>(false);

  constructor(
    public authService: AuthService,
    private dashboardService: DashboardService,
    private router: Router,
    private route: ActivatedRoute,
    private sanitizer: DomSanitizer,
    public translationService: TranslationService,
    private http: HttpClient
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

        this.isLoading.set(false);
        
        // Load users for current dashboard
        const currentDash = this.getCurrentDashboard();
        if (currentDash) {
          this.loadDashboardUsers(currentDash.id);
        }
      },
      error: () => {
        this.errorMessage.set(this.translationService.translate('dashboard.error'));
        this.isLoading.set(false);
      }
    });
  }

  loadDashboardUsers(dashboardId: number): void {
    this.isLoadingUsers.set(true);
    this.http.get<{ users: DashboardUser[], total: number }>(`${environment.apiUrl}/dashboard/${dashboardId}/users`).subscribe({
      next: (response) => {
        this.dashboardUsers.set(response.users);
        this.isLoadingUsers.set(false);
      },
      error: () => {
        this.dashboardUsers.set([]);
        this.isLoadingUsers.set(false);
      }
    });
  }

  toggleUsersPanel(): void {
    const newState = !this.showUsersPanel();
    this.showUsersPanel.set(newState);
    
    // Prevent body scroll when modal is open
    if (newState) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    // Note: This method only toggles the modal visibility
    // It does NOT trigger any dashboard refresh
  }

  closeUsersModal(): void {
    this.showUsersPanel.set(false);
    document.body.style.overflow = '';
    // Note: This method only closes the modal
    // It does NOT trigger any dashboard refresh
  }

  getUserInitials(user: DashboardUser): string {
    return ((user.first_name?.[0] || '') + (user.last_name?.[0] || '')).toUpperCase() || '?';
  }

  hasUserImage(user: DashboardUser): boolean {
    return !!(user.profile_image);
  }

  getUserImage(user: DashboardUser): string {
    if (!user.profile_image) return '';
    return user.profile_image.startsWith('data:image') 
      ? user.profile_image 
      : 'data:image/jpeg;base64,' + user.profile_image;
  }

  // Only called by the refresh button — never automatically
  refreshDashboard(): void {
    // Increment the key to force iframe reload
    this.iframeKey.set(this.iframeKey() + 1);
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
