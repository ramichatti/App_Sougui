import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { RolesService } from '../../../core/services/roles.service';
import { AdminService } from '../../../core/services/admin.service';
import { PowerBIService, PowerBIDashboard } from '../../../core/services/powerbi.service';
import { Role, Privilege, User } from '../../../core/models/user.model';
import { NotificationService } from '../../../core/services/notification.service';

@Component({
  selector: 'app-roles-management',
  standalone: true,
  imports: [CommonModule, FormsModule, NavbarComponent],
  templateUrl: './roles-management.component.html',
  styleUrls: ['./roles-management.component.css']
})
export class RolesManagementComponent implements OnInit {
  roles = signal<Role[]>([]);
  privileges = signal<Privilege[]>([]);
  dashboards = signal<PowerBIDashboard[]>([]);
  users = signal<User[]>([]);
  selectedRole = signal<Role | null>(null);
  isLoading = signal<boolean>(false);

  showRoleModal = signal<boolean>(false);
  editingRole = signal<Role | null>(null);
  roleForm = { name: '', description: '', is_admin: false, is_active: true };

  showPrivilegeModal = signal<boolean>(false);
  editingPrivilege = signal<Privilege | null>(null);
  privilegeForm = { name: '', description: '', dashboard_id: null as number | null };

  selectedPrivilegeId: number | null = null;
  selectedUserId: number | null = null;
  userRoleChanges: Record<number, number | null> = {};
  roleSearch = '';

  activeTab: 'roles' | 'privileges' | 'users' = 'roles';

  constructor(
    private rolesService: RolesService,
    private adminService: AdminService,
    private powerbiService: PowerBIService,
    private notif: NotificationService
  ) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.isLoading.set(true);
    this.rolesService.getRoles().subscribe({
      next: (res) => {
        this.roles.set(res.roles);
        const sel = this.selectedRole();
        if (sel) {
          const updated = res.roles.find(r => r.id === sel.id);
          this.selectedRole.set(updated || null);
        }
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false)
    });
    this.rolesService.getPrivileges().subscribe({
      next: (res) => this.privileges.set(res.privileges)
    });
    this.powerbiService.getAllDashboards().subscribe({
      next: (res) => this.dashboards.set(res.dashboards)
    });
    this.adminService.getUsers().subscribe({
      next: (res) => {
        this.users.set(res.users);
        const map: Record<number, number | null> = {};
        res.users.forEach(u => { map[u.id] = u.role_id; });
        this.userRoleChanges = map;
      }
    });
  }

  // ── Stats ──────────────────────────────────────────────────────────────────

  filteredRoles(): Role[] {
    const q = this.roleSearch.toLowerCase().trim();
    if (!q) return this.roles();
    return this.roles().filter(r =>
      r.name.toLowerCase().includes(q) || (r.description || '').toLowerCase().includes(q)
    );
  }

  get totalRoles(): number { return this.roles().length; }
  get totalPrivileges(): number { return this.privileges().length; }
  get totalUsers(): number { return this.users().length; }

  // ── Roles ──────────────────────────────────────────────────────────────────

  openRoleModal(role?: Role): void {
    if (role) {
      this.editingRole.set(role);
      this.roleForm = { name: role.name, description: role.description || '', is_admin: role.is_admin, is_active: role.is_active };
    } else {
      this.editingRole.set(null);
      this.roleForm = { name: '', description: '', is_admin: false, is_active: true };
    }
    this.showRoleModal.set(true);
  }

  closeRoleModal(): void {
    this.showRoleModal.set(false);
    this.editingRole.set(null);
  }

  saveRole(): void {
    const editing = this.editingRole();
    if (editing) {
      this.rolesService.updateRole(editing.id, this.roleForm).subscribe({
        next: () => { this.notif.success('Rôle mis à jour'); this.closeRoleModal(); this.load(); },
        error: (err) => this.notif.error(err.error?.error || 'Erreur lors de la mise à jour')
      });
    } else {
      this.rolesService.createRole(this.roleForm).subscribe({
        next: () => { this.notif.success('Rôle créé'); this.closeRoleModal(); this.load(); },
        error: (err) => this.notif.error(err.error?.error || 'Erreur lors de la création')
      });
    }
  }

  deleteRole(role: Role): void {
    if (role.is_system) { this.notif.error('Les rôles système ne peuvent pas être supprimés'); return; }
    if (!confirm(`Supprimer le rôle "${role.name}" ?`)) return;
    this.rolesService.deleteRole(role.id).subscribe({
      next: () => {
        this.notif.success('Rôle supprimé');
        if (this.selectedRole()?.id === role.id) this.selectedRole.set(null);
        this.load();
      },
      error: (err) => this.notif.error(err.error?.error || 'Erreur lors de la suppression')
    });
  }

  selectRole(role: Role): void {
    this.selectedRole.set(this.selectedRole()?.id === role.id ? null : role);
    this.selectedPrivilegeId = null;
    this.selectedUserId = null;
  }

  closeDetail(): void {
    this.selectedRole.set(null);
    this.selectedPrivilegeId = null;
    this.selectedUserId = null;
  }

  // ── Privilege assignment ───────────────────────────────────────────────────

  assignPrivilege(): void {
    const role = this.selectedRole();
    if (!role || !this.selectedPrivilegeId) return;
    this.rolesService.assignPrivilege(role.id, this.selectedPrivilegeId).subscribe({
      next: () => { this.notif.success('Privilège assigné'); this.selectedPrivilegeId = null; this.load(); },
      error: (err) => this.notif.error(err.error?.error || 'Erreur')
    });
  }

  removePrivilege(role: Role, privilege: Privilege): void {
    this.rolesService.removePrivilege(role.id, privilege.id).subscribe({
      next: () => { this.notif.success('Privilège retiré'); this.load(); },
      error: (err) => this.notif.error(err.error?.error || 'Erreur')
    });
  }

  unassignedPrivileges(): Privilege[] {
    const role = this.selectedRole();
    if (!role?.privileges) return this.privileges();
    const assignedIds = new Set(role.privileges.map(p => p.id));
    return this.privileges().filter(p => !assignedIds.has(p.id));
  }

  // ── User ↔ Role assignment ─────────────────────────────────────────────────

  getUsersForRole(role: Role): User[] {
    return this.users().filter(u => u.role_id === role.id);
  }

  getUsersNotInRole(role: Role): User[] {
    return this.users().filter(u => u.role_id !== role.id);
  }

  assignUserToCurrentRole(): void {
    const role = this.selectedRole();
    if (!role || !this.selectedUserId) return;
    this.adminService.updateUser(this.selectedUserId, { role_id: role.id }).subscribe({
      next: () => { this.notif.success('Utilisateur assigné au rôle'); this.selectedUserId = null; this.load(); },
      error: (err) => this.notif.error(err.error?.error || 'Erreur')
    });
  }

  removeUserFromRole(user: User): void {
    if (!confirm(`Retirer ${user.first_name} ${user.last_name} de ce rôle ?`)) return;
    this.adminService.updateUser(user.id, { role_id: null }).subscribe({
      next: () => { this.notif.success('Utilisateur retiré du rôle'); this.load(); },
      error: (err) => this.notif.error(err.error?.error || 'Erreur')
    });
  }

  saveUserRole(userId: number): void {
    const newRoleId = this.userRoleChanges[userId];
    this.adminService.updateUser(userId, { role_id: newRoleId }).subscribe({
      next: () => { this.notif.success('Rôle mis à jour'); this.load(); },
      error: (err) => this.notif.error(err.error?.error || 'Erreur')
    });
  }

  hasRoleChanged(userId: number, currentRoleId: number | null): boolean {
    return this.userRoleChanges[userId] !== currentRoleId;
  }

  getUserInitials(user: User): string {
    return `${(user.first_name[0] || '').toUpperCase()}${(user.last_name[0] || '').toUpperCase()}`;
  }

  getRoleName(roleId: number | null): string {
    if (!roleId) return 'Aucun rôle';
    return this.roles().find(r => r.id === roleId)?.name ?? 'Rôle inconnu';
  }

  isPrivilegeInRole(role: Role, privilegeId: number): boolean {
    return role.privileges?.some(p => p.id === privilegeId) ?? false;
  }

  getRoleColor(roleId: number | null): string {
    if (!roleId) return '#9ca3af';
    const role = this.roles().find(r => r.id === roleId);
    if (!role) return '#9ca3af';
    if (role.is_admin) return '#1e3a8a';
    const colors = ['#059669', '#d97706', '#7c3aed', '#db2777', '#0891b2'];
    return colors[role.id % colors.length];
  }

  // ── Privileges CRUD ────────────────────────────────────────────────────────

  openPrivilegeModal(privilege?: Privilege): void {
    if (privilege) {
      this.editingPrivilege.set(privilege);
      this.privilegeForm = { name: privilege.name, description: privilege.description || '', dashboard_id: privilege.dashboard_id };
    } else {
      this.editingPrivilege.set(null);
      this.privilegeForm = { name: '', description: '', dashboard_id: null };
    }
    this.showPrivilegeModal.set(true);
  }

  closePrivilegeModal(): void {
    this.showPrivilegeModal.set(false);
    this.editingPrivilege.set(null);
  }

  savePrivilege(): void {
    const editing = this.editingPrivilege();
    const payload = { ...this.privilegeForm, dashboard_id: this.privilegeForm.dashboard_id || null };
    if (editing) {
      this.rolesService.updatePrivilege(editing.id, payload).subscribe({
        next: () => { this.notif.success('Privilège mis à jour'); this.closePrivilegeModal(); this.load(); },
        error: (err) => this.notif.error(err.error?.error || 'Erreur')
      });
    } else {
      this.rolesService.createPrivilege(payload).subscribe({
        next: () => { this.notif.success('Privilège créé'); this.closePrivilegeModal(); this.load(); },
        error: (err) => this.notif.error(err.error?.error || 'Erreur')
      });
    }
  }

  deletePrivilege(privilege: Privilege): void {
    if (!confirm(`Supprimer le privilège "${privilege.name}" ?`)) return;
    this.rolesService.deletePrivilege(privilege.id).subscribe({
      next: () => { this.notif.success('Privilège supprimé'); this.load(); },
      error: (err) => this.notif.error(err.error?.error || 'Erreur')
    });
  }
}
