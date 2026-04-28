import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { AdminService } from '../../../core/services/admin.service';
import { AuthService } from '../../../core/services/auth.service';
import { User, Role } from '../../../core/models/user.model';
import { NotificationService } from '../../../core/services/notification.service';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent],
  templateUrl: './users.component.html',
  styleUrls: ['./users.component.css']
})
export class UsersComponent implements OnInit {
  users = signal<User[]>([]);
  roles = signal<Role[]>([]);
  showModal = signal<boolean>(false);
  editingUser = signal<User | null>(null);
  isLoading = signal<boolean>(false);
  isSaving = signal<boolean>(false);

  searchTerm = '';
  selectedRoleFilter = 'all';
  selectedFile: File | null = null;
  previewImage: string | null = null;
  viewMode: 'grid' | 'list' = 'grid';

  userForm = {
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role_id: null as number | null,
    is_active: true,
    profile_image: ''
  };

  constructor(
    private adminService: AdminService,
    private authService: AuthService,
    private notif: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadUsers();
    this.loadRoles();
  }

  // ── Data loading ────────────────────────────────────────────────────────────

  loadRoles(): void {
    this.adminService.getRoles().subscribe({
      next: (res) => this.roles.set(res.roles)
    });
  }

  loadUsers(): void {
    this.isLoading.set(true);
    this.adminService.getUsers().subscribe({
      next: (res) => { this.users.set(res.users); this.isLoading.set(false); },
      error: () => this.isLoading.set(false)
    });
  }

  // ── Filtering ───────────────────────────────────────────────────────────────

  getFilteredUsers(): User[] {
    let list = this.users();
    if (this.selectedRoleFilter !== 'all') {
      list = list.filter(u => u.role === this.selectedRoleFilter);
    }
    const q = this.searchTerm.toLowerCase().trim();
    if (q) {
      list = list.filter(u =>
        u.first_name.toLowerCase().includes(q) ||
        u.last_name.toLowerCase().includes(q) ||
        u.email.toLowerCase().includes(q)
      );
    }
    return list;
  }

  setFilter(role: string): void { this.selectedRoleFilter = role; }
  clearSearch(): void { this.searchTerm = ''; }
  setViewMode(mode: 'grid' | 'list'): void { this.viewMode = mode; }

  // ── Stats ───────────────────────────────────────────────────────────────────

  get totalCount(): number { return this.users().length; }
  get activeCount(): number { return this.users().filter(u => u.is_active).length; }
  get adminCount(): number { return this.users().filter(u => u.is_admin).length; }
  get inactiveCount(): number { return this.users().filter(u => !u.is_active).length; }

  // ── Avatar helpers ──────────────────────────────────────────────────────────

  hasUserImage(user: User): boolean {
    return !!(user.profile_image);
  }

  getUserImage(user: User): string {
    if (!user.profile_image) return '';
    return user.profile_image.startsWith('data:image')
      ? user.profile_image
      : 'data:image/jpeg;base64,' + user.profile_image;
  }

  getUserInitials(user: User): string {
    return ((user.first_name?.[0] || '') + (user.last_name?.[0] || '')).toUpperCase() || '?';
  }

  hasPreviewImage(): boolean {
    if (this.previewImage) return true;
    return !!(this.editingUser()?.profile_image);
  }

  getPreviewImage(): string {
    if (this.previewImage) return this.previewImage;
    const img = this.editingUser()?.profile_image;
    if (!img) return '';
    return img.startsWith('data:image') ? img : 'data:image/jpeg;base64,' + img;
  }

  getPreviewInitials(): string {
    const u = this.editingUser();
    if (u) return this.getUserInitials(u);
    return this.userForm.first_name?.[0]?.toUpperCase() || '?';
  }

  // ── File selection ──────────────────────────────────────────────────────────

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      this.notif.error('Format invalide. Utilisez JPG, PNG, GIF ou WebP.');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      this.notif.error('Image trop volumineuse. Taille maximale : 5 MB.');
      return;
    }
    this.selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e: any) => {
      this.previewImage = e.target.result;
      this.userForm.profile_image = e.target.result.split(',')[1];
    };
    reader.readAsDataURL(file);
  }

  // ── Modal ───────────────────────────────────────────────────────────────────

  openModal(user?: User): void {
    if (user) {
      this.editingUser.set(user);
      this.userForm = {
        email: user.email,
        password: '',
        first_name: user.first_name,
        last_name: user.last_name,
        role_id: user.role_id,
        is_active: user.is_active,
        profile_image: user.profile_image || ''
      };
    } else {
      this.editingUser.set(null);
      this.resetForm();
    }
    this.previewImage = null;
    this.selectedFile = null;
    this.showModal.set(true);
  }

  closeModal(): void {
    this.showModal.set(false);
    this.selectedFile = null;
    this.previewImage = null;
    this.editingUser.set(null);
  }

  // ── Save / Delete ───────────────────────────────────────────────────────────

  saveUser(): void {
    if (!this.userForm.first_name.trim() || !this.userForm.last_name.trim()) {
      this.notif.error('Le prénom et le nom sont requis.');
      return;
    }
    if (!this.userForm.email.trim()) {
      this.notif.error('L\'email est requis.');
      return;
    }
    if (!this.editingUser() && !this.userForm.password) {
      this.notif.error('Le mot de passe est requis pour un nouvel utilisateur.');
      return;
    }
    if (!this.userForm.role_id) {
      this.notif.error('Veuillez sélectionner un rôle.');
      return;
    }

    this.isSaving.set(true);
    const editing = this.editingUser();
    const currentUser = this.authService.currentUser();

    if (editing) {
      this.adminService.updateUser(editing.id, this.userForm).subscribe({
        next: (res) => {
          this.isSaving.set(false);
          if (currentUser && editing.id === currentUser.id) {
            const updated = {
              ...currentUser,
              first_name: this.userForm.first_name,
              last_name: this.userForm.last_name,
              email: this.userForm.email,
              profile_image: res.user?.profile_image || currentUser.profile_image
            };
            this.authService.currentUser.set(updated);
            localStorage.setItem('user', JSON.stringify(updated));
          }
          this.notif.success('Utilisateur mis à jour avec succès');
          this.closeModal();
          this.loadUsers();
        },
        error: (err) => {
          this.isSaving.set(false);
          this.notif.error(err.error?.error || 'Erreur lors de la mise à jour');
        }
      });
    } else {
      this.adminService.createUser(this.userForm).subscribe({
        next: () => {
          this.isSaving.set(false);
          this.notif.success('Utilisateur créé avec succès');
          this.closeModal();
          this.loadUsers();
        },
        error: (err) => {
          this.isSaving.set(false);
          this.notif.error(err.error?.error || 'Erreur lors de la création');
        }
      });
    }
  }

  deleteUser(user: User): void {
    if (!confirm(`Supprimer l'utilisateur « ${user.first_name} ${user.last_name} » ? Cette action est irréversible.`)) return;
    this.adminService.deleteUser(user.id).subscribe({
      next: () => { this.notif.success('Utilisateur supprimé'); this.loadUsers(); },
      error: (err) => this.notif.error(err.error?.error || 'Erreur lors de la suppression')
    });
  }

  getRoleName(roleId: number | null): string {
    if (!roleId) return '—';
    return this.roles().find(r => r.id === roleId)?.name ?? '—';
  }

  private resetForm(): void {
    this.userForm = {
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      role_id: this.roles()[0]?.id ?? null,
      is_active: true,
      profile_image: ''
    };
  }
}
