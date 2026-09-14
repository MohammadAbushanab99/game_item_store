import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';

// Blocks pages for anonymous users, redirecting to /login with a returnUrl.
export const authGuard: CanActivateFn = (_route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  return auth.token()
    ? true
    : router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } });
};
