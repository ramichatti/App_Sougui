import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../core/services/auth.service';
import { ProfileService } from '../../core/services/profile.service';
import { TranslationService } from '../../core/services/translation.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit {
  profileForm = {
    first_name: '',
    last_name: '',
    email: ''
  };

  passwordForm = {
    current_password: '',
    new_password: '',
    confirm_password: ''
  };

  selectedFile: File | null = null;
  imagePreview: string | null = null;
  showPasswordForm = signal<boolean>(false);
  codeVerified = signal<boolean>(false);
  verificationCode: string = '';

  message = signal<string>('');
  errorMessage = signal<string>('');
  isLoading = signal<boolean>(false);

  constructor(
    public authService: AuthService,
    private profileService: ProfileService,
    public translate: TranslationService
  ) {}

  ngOnInit(): void {
    this.loadProfile();
  }

  loadProfile(): void {
    const user = this.authService.currentUser();
    if (user) {
      this.profileForm = {
        first_name: user.first_name,
        last_name: user.last_name,
        email: user.email
      };
      
      if (user.profile_image) {
        this.imagePreview = 'data:image/jpeg;base64,' + user.profile_image;
      }
    }
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
      if (!validTypes.includes(file.type)) {
        this.errorMessage.set('Format d\'image non valide. Utilisez JPG, PNG, GIF ou WebP.');
        return;
      }

      // Validate file size (5MB max)
      const maxSize = 5 * 1024 * 1024; // 5MB in bytes
      if (file.size > maxSize) {
        this.errorMessage.set('L\'image est trop volumineuse. Taille maximale: 5MB.');
        return;
      }

      this.selectedFile = file;
      this.errorMessage.set('');
      
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.imagePreview = e.target.result;
      };
      reader.readAsDataURL(file);
    }
  }

  uploadImage(): void {
    if (!this.imagePreview) {
      this.errorMessage.set('Veuillez sélectionner une image');
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set('');
    this.message.set('');

    this.profileService.uploadImage(this.imagePreview).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        this.message.set('Photo de profil mise à jour');
        
        // Update local user data with the new image
        const user = this.authService.currentUser();
        if (user && this.imagePreview) {
          // Update with the base64 image from response
          user.profile_image = response.profile_image || this.imagePreview.split(',')[1];
          localStorage.setItem('user', JSON.stringify(user));
          this.authService.currentUser.set({...user}); // Create new reference to trigger change detection
        }
        
        // Clear preview and file after successful upload
        this.selectedFile = null;
        // Keep the preview to show the uploaded image
        setTimeout(() => {
          this.loadProfile();
        }, 100);
      },
      error: (error) => {
        this.isLoading.set(false);
        this.errorMessage.set(error.error?.error || error.error?.message || 'Erreur lors du téléchargement');
      }
    });
  }

  hasProfileImage(): boolean {
    if (this.imagePreview && this.selectedFile) return true;
    const user = this.authService.currentUser();
    return !!(user?.profile_image);
  }

  getProfileImage(): string {
    if (this.imagePreview && this.selectedFile) return this.imagePreview;
    const user = this.authService.currentUser();
    if (user?.profile_image) {
      return user.profile_image.startsWith('data:image')
        ? user.profile_image
        : 'data:image/jpeg;base64,' + user.profile_image;
    }
    return '';
  }

  getUserInitials(): string {
    const user = this.authService.currentUser();
    return ((user?.first_name?.[0] || '') + (user?.last_name?.[0] || '')).toUpperCase() || '?';
  }

  updateProfile(): void {
    // Validate first name
    if (!this.profileForm.first_name || !this.profileForm.first_name.trim()) {
      this.errorMessage.set('Le prénom est requis');
      return;
    }

    if (this.profileForm.first_name.trim().length < 2) {
      this.errorMessage.set('Le prénom doit contenir au moins 2 caractères');
      return;
    }

    // Validate last name
    if (!this.profileForm.last_name || !this.profileForm.last_name.trim()) {
      this.errorMessage.set('Le nom est requis');
      return;
    }

    if (this.profileForm.last_name.trim().length < 2) {
      this.errorMessage.set('Le nom doit contenir au moins 2 caractères');
      return;
    }

    // Validate email
    if (!this.profileForm.email || !this.profileForm.email.trim()) {
      this.errorMessage.set('L\'email est requis');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.profileForm.email)) {
      this.errorMessage.set('Format d\'email invalide');
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set('');
    this.message.set('');

    this.profileService.updateProfile(this.profileForm).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        this.message.set('Profil mis à jour avec succès');
        
        // Update local user data
        const user = this.authService.currentUser();
        if (user) {
          user.first_name = this.profileForm.first_name;
          user.last_name = this.profileForm.last_name;
          user.email = this.profileForm.email;
          localStorage.setItem('user', JSON.stringify(user));
          this.authService.currentUser.set({...user}); // Create new reference to trigger change detection
        }
      },
      error: (error) => {
        this.isLoading.set(false);
        this.errorMessage.set(error.error?.error || error.error?.message || 'Erreur lors de la mise à jour');
      }
    });
  }

  requestPasswordChange(): void {
    this.isLoading.set(true);
    this.errorMessage.set('');
    this.message.set('');

    this.profileService.requestPasswordChange().subscribe({
      next: (response) => {
        this.isLoading.set(false);
        this.showPasswordForm.set(true);
        this.message.set('Code de vérification envoyé à votre email');
        
        // For development - show code in console
        if (response.debug_code) {
          console.log('Verification code:', response.debug_code);
        }
      },
      error: (error) => {
        this.isLoading.set(false);
        this.errorMessage.set(error.error?.error || error.error?.message || 'Erreur lors de l\'envoi du code');
      }
    });
  }

  verifyCode(): void {
    if (!this.verificationCode || this.verificationCode.length !== 6) {
      this.errorMessage.set('Veuillez entrer un code à 6 chiffres');
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set('');
    this.message.set('');

    this.profileService.verifyPasswordChangeCode(this.verificationCode).subscribe({
      next: () => {
        this.isLoading.set(false);
        this.codeVerified.set(true);
        this.message.set('Code vérifié avec succès');
      },
      error: (error) => {
        this.isLoading.set(false);
        this.errorMessage.set(error.error?.error || error.error?.message || 'Code invalide ou expiré');
      }
    });
  }

  changePassword(): void {
    // Validate current password
    if (!this.passwordForm.current_password || !this.passwordForm.current_password.trim()) {
      this.errorMessage.set('Le mot de passe actuel est requis');
      return;
    }

    // Validate new password
    if (!this.passwordForm.new_password || !this.passwordForm.new_password.trim()) {
      this.errorMessage.set('Le nouveau mot de passe est requis');
      return;
    }

    if (this.passwordForm.new_password.length < 6) {
      this.errorMessage.set('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }

    // Check password strength
    const hasUpperCase = /[A-Z]/.test(this.passwordForm.new_password);
    const hasLowerCase = /[a-z]/.test(this.passwordForm.new_password);
    const hasNumber = /[0-9]/.test(this.passwordForm.new_password);
    
    if (!hasUpperCase || !hasLowerCase || !hasNumber) {
      this.errorMessage.set('Le mot de passe doit contenir au moins une majuscule, une minuscule et un chiffre');
      return;
    }

    // Validate confirm password
    if (!this.passwordForm.confirm_password || !this.passwordForm.confirm_password.trim()) {
      this.errorMessage.set('La confirmation du mot de passe est requise');
      return;
    }

    if (this.passwordForm.new_password !== this.passwordForm.confirm_password) {
      this.errorMessage.set('Les mots de passe ne correspondent pas');
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set('');
    this.message.set('');

    this.profileService.changePasswordWithCode({
      code: this.verificationCode,
      current_password: this.passwordForm.current_password,
      new_password: this.passwordForm.new_password
    }).subscribe({
      next: () => {
        this.isLoading.set(false);
        this.message.set('Mot de passe modifié avec succès! Un email de confirmation a été envoyé.');
        this.passwordForm = {
          current_password: '',
          new_password: '',
          confirm_password: ''
        };
        this.showPasswordForm.set(false);
        this.codeVerified.set(false);
        this.verificationCode = '';
      },
      error: (error) => {
        this.isLoading.set(false);
        this.errorMessage.set(error.error?.error || error.error?.message || 'Erreur lors du changement de mot de passe');
      }
    });
  }

  cancelPasswordChange(): void {
    this.showPasswordForm.set(false);
    this.codeVerified.set(false);
    this.verificationCode = '';
    this.passwordForm = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    };
    this.errorMessage.set('');
    this.message.set('');
  }
}
