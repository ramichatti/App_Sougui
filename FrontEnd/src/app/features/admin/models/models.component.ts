import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';

@Component({
  selector: 'app-models',
  standalone: true,
  imports: [CommonModule, RouterLink, NavbarComponent],
  template: `
    <app-navbar></app-navbar>
    <div class="models-page">
      <div class="models-header">
        <div class="header-content">
          <h1>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
            </svg>
            Modèles ML
          </h1>
          <p>Modèles de Machine Learning pour l'analyse et la prédiction</p>
        </div>
      </div>

      <div class="models-grid">
        <div class="model-card" *ngFor="let model of models" (click)="navigateToModel(model.route)">
          <div class="model-icon" [style.background]="model.gradient">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="white">
              <path [attr.d]="model.icon"/>
            </svg>
          </div>
          <div class="model-info">
            <h3>{{ model.name }}</h3>
            <p>{{ model.description }}</p>
            <div class="model-meta">
              <span class="model-type">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z"/>
                </svg>
                {{ model.type }}
              </span>
              <span class="model-status status-ready">
                Prêt
              </span>
            </div>
          </div>
          <div class="model-arrow">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 5l7 7-7 7"/>
            </svg>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .models-page {
      min-height: 100vh;
      background: linear-gradient(135deg, #f0f4ff 0%, #e8eeff 50%, #f5f7ff 100%);
      padding-top: 80px;
    }

    .models-header {
      background: linear-gradient(135deg, #059669 0%, #10b981 100%);
      padding: 40px 32px;
      color: white;
    }

    .header-content {
      max-width: 1200px;
      margin: 0 auto;
    }

    .header-content h1 {
      font-size: 28px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 12px;
      margin: 0 0 8px 0;
    }

    .header-content p {
      font-size: 16px;
      opacity: 0.85;
      margin: 0;
    }

    .models-grid {
      max-width: 1200px;
      margin: 32px auto;
      padding: 0 32px;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
      gap: 24px;
    }

    .model-card {
      background: white;
      border-radius: 16px;
      padding: 28px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
      display: flex;
      gap: 20px;
      align-items: center;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      cursor: pointer;
      border: 1px solid rgba(5, 150, 105, 0.08);
    }

    .model-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 30px rgba(5, 150, 105, 0.15);
    }

    .model-icon {
      width: 64px;
      height: 64px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .model-info {
      flex: 1;
      min-width: 0;
    }

    .model-info h3 {
      font-size: 18px;
      font-weight: 600;
      color: #1e293b;
      margin: 0 0 6px 0;
    }

    .model-info p {
      font-size: 14px;
      color: #64748b;
      margin: 0 0 14px 0;
      line-height: 1.5;
    }

    .model-meta {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .model-type {
      display: flex;
      align-items: center;
      gap: 5px;
      font-size: 12px;
      color: #94a3b8;
      text-transform: capitalize;
    }

    .model-status {
      font-size: 11px;
      font-weight: 600;
      padding: 4px 12px;
      border-radius: 20px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .status-ready {
      background: #d1fae5;
      color: #065f46;
    }

    .model-arrow {
      color: #cbd5e1;
      transition: transform 0.2s ease, color 0.2s ease;
    }

    .model-card:hover .model-arrow {
      transform: translateX(4px);
      color: #10b981;
    }
  `]
})
export class ModelsComponent implements OnInit {
  models = [
    {
      name: 'Best Seller Prediction',
      description: 'Prédiction des ventes et identification des produits best-sellers',
      type: 'régression',
      route: '/admin/models/best-seller',
      gradient: 'linear-gradient(135deg, #f59e0b, #fbbf24)',
      icon: 'M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z'
    },
    {
      name: 'K-Means Clustering',
      description: 'Segmentation clients basée sur RFM et comportement d\'achat',
      type: 'clustering',
      route: '/admin/models/kmeans',
      gradient: 'linear-gradient(135deg, #059669, #10b981)',
      icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z'
    }
  ];

  constructor(private router: Router) {}

  ngOnInit(): void {}

  navigateToModel(route: string): void {
    this.router.navigate([route]);
  }
}
