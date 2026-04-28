import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NotificationService } from '../../../core/services/notification.service';

@Component({
  selector: 'app-notification',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="notification-container">
      @for (notification of notificationService.notifications(); track notification.id) {
        <div 
          class="notification notification-{{ notification.type }}"
          (click)="notificationService.remove(notification.id)"
        >
          <div class="notification-icon">
            @switch (notification.type) {
              @case ('success') {
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              }
              @case ('error') {
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              }
              @case ('warning') {
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              }
              @case ('info') {
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
            }
          </div>
          <div class="notification-content">
            <p>{{ notification.message }}</p>
          </div>
          <button 
            class="notification-close"
            (click)="notificationService.remove(notification.id)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      }
    </div>
  `,
  styles: [`
    .notification-container {
      position: fixed;
      top: 90px;
      right: 20px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 12px;
      max-width: 400px;
    }

    .notification {
      display: flex;
      align-items: start;
      gap: 12px;
      padding: 16px;
      border-radius: 12px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
      animation: slideInRight 0.3s ease;
      cursor: pointer;
      transition: all 0.2s ease;
      min-width: 320px;
    }

    .notification:hover {
      transform: translateX(-4px);
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
    }

    @keyframes slideInRight {
      from {
        opacity: 0;
        transform: translateX(100%);
      }
      to {
        opacity: 1;
        transform: translateX(0);
      }
    }

    .notification-success {
      background-color: #d1fae5;
      color: #065f46;
      border-left: 4px solid #10b981;
    }

    .notification-error {
      background-color: #fee2e2;
      color: #991b1b;
      border-left: 4px solid #ef4444;
    }

    .notification-warning {
      background-color: #fef3c7;
      color: #92400e;
      border-left: 4px solid #f59e0b;
    }

    .notification-info {
      background-color: #dbeafe;
      color: #1e40af;
      border-left: 4px solid #3b82f6;
    }

    .notification-icon {
      flex-shrink: 0;
      width: 24px;
      height: 24px;
    }

    .notification-icon svg {
      width: 100%;
      height: 100%;
    }

    .notification-content {
      flex: 1;
    }

    .notification-content p {
      margin: 0;
      font-size: 14px;
      font-weight: 500;
      line-height: 1.5;
    }

    .notification-close {
      flex-shrink: 0;
      width: 20px;
      height: 20px;
      background: none;
      border: none;
      cursor: pointer;
      opacity: 0.6;
      transition: opacity 0.2s ease;
      padding: 0;
    }

    .notification-close:hover {
      opacity: 1;
    }

    .notification-close svg {
      width: 100%;
      height: 100%;
    }

    @media (max-width: 768px) {
      .notification-container {
        left: 20px;
        right: 20px;
        max-width: none;
      }

      .notification {
        min-width: auto;
      }
    }
  `]
})
export class NotificationComponent {
  constructor(public notificationService: NotificationService) {}
}
