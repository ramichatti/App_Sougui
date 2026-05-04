import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AdminSecurityService } from '../services/admin-security.service';
import { AuthService } from '../services/auth.service';

export const adminSecurityGuard: CanActivateFn = (route, state) => {
  const security = inject(AdminSecurityService);
  const auth = inject(AuthService);
  const router = inject(Router);

  if (!auth.isAdmin()) {
    router.navigate(['/home']);
    return false;
  }

  if (security.isVerified()) {
    return true;
  }

  router.navigate(['/admin/confirm'], {
    queryParams: { return: state.url }
  });
  return false;
};
