import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { EmailSettingsService, EmailSettings } from '../../../core/services/email-settings.service';
import { NotificationService } from '../../../core/services/notification.service';
import { TranslationService } from '../../../core/services/translation.service';

@Component({
  selector: 'app-email-settings',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent],
  templateUrl: './email-settings.component.html',
  styleUrls: ['./email-settings.component.css']
})
export class EmailSettingsComponent implements OnInit {
  settings = signal<EmailSettings>({
    mail_server: 'smtp.gmail.com',
    mail_port: 587,
    mail_use_tls: true,
    mail_username: '',
    mail_password: '',
    is_configured: false,
    last_updated: null,
    updated_by: null
  });

  isLoading = signal(false);
  isTesting = signal(false);
  isSaving = signal(false);
  showPassword = signal(false);
  testRecipient = signal('');
  testResult = signal<{ success: boolean; message: string } | null>(null);

  constructor(
    private emailService: EmailSettingsService,
    private notif: NotificationService,
    public translate: TranslationService
  ) {}

  ngOnInit(): void {
    this.loadSettings();
  }

  private getErrorMessage(err: any, fallback: string): string {
    const apiMsg = err?.error?.message || err?.error?.error;
    if (apiMsg) return apiMsg;
    if (err?.status === 0) return 'Impossible de contacter le serveur (CORS/serveur arrêté)';
    if (err?.status === 401) return 'Session expirée. Veuillez vous reconnecter.';
    if (err?.status === 403) return 'Accès refusé. Permissions administrateur requises.';
    return fallback;
  }

  loadSettings(): void {
    this.isLoading.set(true);
    this.emailService.getSettings().subscribe({
      next: (data) => {
        this.settings.set(data);
        this.testRecipient.set(data.mail_username);
        this.isLoading.set(false);
      },
      error: (err) => {
        this.notif.error(this.getErrorMessage(err, 'Erreur lors du chargement des paramètres'));
        this.isLoading.set(false);
      }
    });
  }

  testConnection(): void {
    const current = this.settings();
    
    if (!current.mail_server || !current.mail_port || !current.mail_username || !current.mail_password) {
      this.notif.error('Veuillez remplir tous les champs');
      return;
    }

    if (current.mail_password === '********') {
      this.notif.error('Veuillez entrer le mot de passe réel pour tester');
      return;
    }

    this.isTesting.set(true);
    this.testResult.set(null);

    this.emailService.testConnection({
      mail_server: current.mail_server,
      mail_port: current.mail_port,
      mail_use_tls: current.mail_use_tls,
      mail_username: current.mail_username,
      mail_password: current.mail_password,
      test_recipient: this.testRecipient() || current.mail_username
    }).subscribe({
      next: (response) => {
        this.isTesting.set(false);
        if (response.success) {
          this.testResult.set({
            success: true,
            message: response.message || 'Test réussi!'
          });
          this.notif.success(response.message || 'Connexion SMTP réussie!');
        } else {
          this.testResult.set({
            success: false,
            message: response.message || response.error || 'Test échoué'
          });
          this.notif.error(response.message || 'Test de connexion échoué');
        }
      },
      error: (err) => {
        this.isTesting.set(false);
        const errorMsg = this.getErrorMessage(err, 'Erreur lors du test');
        this.testResult.set({
          success: false,
          message: errorMsg
        });
        this.notif.error(errorMsg);
      }
    });
  }

  saveSettings(): void {
    const current = this.settings();
    
    if (!current.mail_server || !current.mail_port || !current.mail_username) {
      this.notif.error('Veuillez remplir tous les champs obligatoires');
      return;
    }

    this.isSaving.set(true);

    this.emailService.updateSettings(current).subscribe({
      next: (response) => {
        this.isSaving.set(false);
        this.notif.success('Paramètres email sauvegardés avec succès');
        this.loadSettings(); // Recharger pour obtenir les données à jour
      },
      error: (err) => {
        this.isSaving.set(false);
        this.notif.error(this.getErrorMessage(err, 'Erreur lors de la sauvegarde'));
      }
    });
  }

  togglePasswordVisibility(): void {
    this.showPassword.update(v => !v);
  }

  updateServer(value: string): void {
    this.settings.update(s => ({ ...s, mail_server: value }));
  }

  updatePort(value: string): void {
    this.settings.update(s => ({ ...s, mail_port: parseInt(value) || 587 }));
  }

  updateUsername(value: string): void {
    this.settings.update(s => ({ ...s, mail_username: value }));
  }

  updatePassword(value: string): void {
    this.settings.update(s => ({ ...s, mail_password: value }));
  }

  toggleTLS(): void {
    this.settings.update(s => ({ ...s, mail_use_tls: !s.mail_use_tls }));
  }
}
