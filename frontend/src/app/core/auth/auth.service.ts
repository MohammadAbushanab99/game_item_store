import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, map, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { CartService } from '../cart/cart.service';
import { TokenResponse } from '../models/api.models';

const STORAGE_KEY = 'game_store_token';

// Keeps the JWT in sessionStorage and checks its expiry before every request.
@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly cart = inject(CartService);

  private readonly tokenSignal = signal<string | null>(this.readStoredToken());
  readonly isLoggedIn = computed(() => this.tokenSignal() !== null);
  readonly isAdmin = computed(() => {
    const token = this.tokenSignal();
    return token ? this.parseJwt(token)?.is_admin === true : false;
  });

  login(username: string, password: string): Observable<void> {
    return this.http
      .post<TokenResponse>(`${environment.apiUrl}/auth/login`, { username, password })
      .pipe(
        tap((res) => {
          sessionStorage.setItem(STORAGE_KEY, res.access_token);
          this.tokenSignal.set(res.access_token);
        }),
        map(() => undefined),
      );
  }

  token(): string | null {
    const token = this.tokenSignal();
    if (token && this.isExpired(token)) {
      this.clear();
      return null;
    }
    return token;
  }

  logout(): void {
    this.clear();
    this.router.navigate(['/login']);
  }

  private clear(): void {
    sessionStorage.removeItem(STORAGE_KEY);
    this.tokenSignal.set(null);
    this.cart.clear();
  }

  private readStoredToken(): string | null {
    const token = sessionStorage.getItem(STORAGE_KEY);
    return token && !this.isExpired(token) ? token : null;
  }

  private isExpired(token: string): boolean {
    const payload = this.parseJwt(token);
    return !payload || payload.exp * 1000 <= Date.now();
  }

  private parseJwt(token: string): { exp: number; is_admin?: boolean } | null {
    try {
      return JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
    } catch {
      return null;
    }
  }
}
