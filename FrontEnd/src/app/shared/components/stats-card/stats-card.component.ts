import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-stats-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="stats-card" [class.clickable]="clickable" (click)="handleClick()">
      <div class="stats-icon" [style.background]="iconBg">
        {{ icon }}
      </div>
      <div class="stats-content">
        <div class="stats-value">{{ value }}</div>
        <div class="stats-label">{{ label }}</div>
        @if (change !== undefined) {
          <div class="stats-change" [class.positive]="change >= 0" [class.negative]="change < 0">
            <span class="change-icon">{{ change >= 0 ? '↑' : '↓' }}</span>
            <span>{{ Math.abs(change) }}%</span>
          </div>
        }
      </div>
    </div>
  `,
  styles: [`
    .stats-card {
      background: white;
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      display: flex;
      align-items: center;
      gap: 20px;
      transition: all 0.3s ease;
    }

    .stats-card.clickable {
      cursor: pointer;
    }

    .stats-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }

    .stats-icon {
      width: 64px;
      height: 64px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 32px;
      flex-shrink: 0;
    }

    .stats-content {
      flex: 1;
    }

    .stats-value {
      font-size: 32px;
      font-weight: 800;
      color: #1e3a8a;
      line-height: 1;
      margin-bottom: 8px;
    }

    .stats-label {
      font-size: 14px;
      color: #6b7280;
      font-weight: 500;
      margin-bottom: 8px;
    }

    .stats-change {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 8px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
    }

    .stats-change.positive {
      background-color: #d1fae5;
      color: #065f46;
    }

    .stats-change.negative {
      background-color: #fee2e2;
      color: #991b1b;
    }

    .change-icon {
      font-size: 16px;
    }

    @media (max-width: 768px) {
      .stats-card {
        padding: 20px;
      }

      .stats-icon {
        width: 56px;
        height: 56px;
        font-size: 28px;
      }

      .stats-value {
        font-size: 28px;
      }
    }
  `]
})
export class StatsCardComponent {
  @Input() icon: string = '📊';
  @Input() value: string | number = '0';
  @Input() label: string = '';
  @Input() iconBg: string = '#dbeafe';
  @Input() change?: number;
  @Input() clickable: boolean = false;

  Math = Math;

  handleClick(): void {
    if (this.clickable) {
      // Emit event or handle click
    }
  }
}
