import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Role, Privilege } from '../models/user.model';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class RolesService {
  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // ── Roles ─────────────────────────────────────────────────────────────────

  getRoles(): Observable<{ roles: Role[] }> {
    return this.http.get<{ roles: Role[] }>(`${this.api}/roles`);
  }

  createRole(data: Partial<Role>): Observable<{ message?: string; role: Role }> {
    return this.http.post<{ message?: string; role: Role }>(`${this.api}/roles`, data);
  }

  updateRole(id: number, data: Partial<Role>): Observable<{ message?: string; role: Role }> {
    return this.http.put<{ message?: string; role: Role }>(`${this.api}/roles/${id}`, data);
  }

  deleteRole(id: number): Observable<any> {
    return this.http.delete(`${this.api}/roles/${id}`);
  }

  // ── Privilege assignment ───────────────────────────────────────────────────

  assignPrivilege(roleId: number, privilegeId: number): Observable<{ role: Role }> {
    return this.http.post<{ role: Role }>(`${this.api}/roles/${roleId}/privileges`, { privilege_id: privilegeId });
  }

  removePrivilege(roleId: number, privilegeId: number): Observable<{ role: Role }> {
    return this.http.delete<{ role: Role }>(`${this.api}/roles/${roleId}/privileges/${privilegeId}`);
  }

  // ── Privileges ─────────────────────────────────────────────────────────────

  getPrivileges(): Observable<{ privileges: Privilege[] }> {
    return this.http.get<{ privileges: Privilege[] }>(`${this.api}/roles/privileges`);
  }

  createPrivilege(data: Partial<Privilege>): Observable<{ privilege: Privilege }> {
    return this.http.post<{ privilege: Privilege }>(`${this.api}/roles/privileges`, data);
  }

  updatePrivilege(id: number, data: Partial<Privilege>): Observable<{ privilege: Privilege }> {
    return this.http.put<{ privilege: Privilege }>(`${this.api}/roles/privileges/${id}`, data);
  }

  deletePrivilege(id: number): Observable<any> {
    return this.http.delete(`${this.api}/roles/privileges/${id}`);
  }
}
