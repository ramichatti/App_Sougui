import { Injectable, signal, computed, OnDestroy } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AuthService } from './auth.service';
import { environment } from '../../../environments/environment';

export interface AppNotification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  created_at: string;
}

@Injectable({ providedIn: 'root' })
export class UserNotificationsService implements OnDestroy {
  private apiUrl = `${environment.apiUrl}/notifications`;

  notifications = signal<AppNotification[]>([]);
  unreadCount = computed(() => this.notifications().filter(n => !n.is_read).length);

  private pollInterval: any = null;
  private readonly POLL_MS = 8000; // 8 s — fast enough to feel real-time

  private onVisible = () => {
    if (document.visibilityState === 'visible') {
      this.load();
    }
  };

  constructor(private http: HttpClient, private authService: AuthService) {}

  startPolling(): void {
    this.load();
    if (!this.pollInterval) {
      this.pollInterval = setInterval(() => this.load(), this.POLL_MS);
    }
    document.addEventListener('visibilitychange', this.onVisible);
  }

  stopPolling(): void {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
    document.removeEventListener('visibilitychange', this.onVisible);
    this.notifications.set([]);
  }

  load(): void {
    if (!this.authService.currentUser()) return;

    // Snapshot before the request
    const prevList = this.notifications();
    const isFirstLoad = prevList.length === 0;
    const prevPrivCount = prevList.filter(n => n.type === 'privilege').length;
    const prevMaxId = prevList.reduce((max, n) => Math.max(max, n.id), 0);

    this.http.get<AppNotification[]>(this.apiUrl).subscribe({
      next: (data) => {
        const newPrivCount = data.filter(n => n.type === 'privilege').length;
        const newMaxId = data.reduce((max, n) => Math.max(max, n.id), 0);

        // Only update notifications signal - DO NOT refresh user automatically
        // This prevents unnecessary re-renders of components like PowerBI dashboard
        // User privileges will be refreshed on next login or manual refresh
        this.notifications.set(data);

        // Optional: If you need to refresh user for privilege changes,
        // do it only when user explicitly interacts (clicks notification, etc.)
        // Uncomment below if you want to refresh on new privilege notifications:
        // if (!isFirstLoad && (newPrivCount !== prevPrivCount || newMaxId > prevMaxId)) {
        //   this.authService.refreshUser();
        // }
      },
      error: () => {}
    });
  }

  markRead(notif: AppNotification): void {
    if (notif.is_read) return;
    this.http.put(`${this.apiUrl}/${notif.id}/read`, {}).subscribe({
      next: () => {
        this.notifications.update(list =>
          list.map(n => n.id === notif.id ? { ...n, is_read: true } : n)
        );
        
        // If it's a privilege notification, refresh user to get updated privileges
        if (notif.type === 'privilege') {
          this.authService.refreshUser();
        }
      },
      error: () => {}
    });
  }

  markAllRead(): void {
    this.http.put(`${this.apiUrl}/read-all`, {}).subscribe({
      next: () => {
        this.notifications.update(list => list.map(n => ({ ...n, is_read: true })));
      },
      error: () => {}
    });
  }

  ngOnDestroy(): void {
    this.stopPolling();
  }
}
