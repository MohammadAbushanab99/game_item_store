import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { AuthService } from './auth.service';

function fakeJwt(payload: object): string {
  const b64 = (o: object) => btoa(JSON.stringify(o)).replace(/=+$/, '');
  return `header.${b64(payload)}.sig`;
}

describe('AuthService', () => {
  let auth: AuthService;
  let http: HttpTestingController;

  beforeEach(() => {
    sessionStorage.clear();
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    });
    auth = TestBed.inject(AuthService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('is logged out initially', () => {
    expect(auth.isLoggedIn()).toBeFalse();
    expect(auth.isAdmin()).toBeFalse();
  });

  it('stores the token and reads is_admin from the JWT on login', () => {
    const token = fakeJwt({ exp: Math.floor(Date.now() / 1000) + 3600, is_admin: true });
    auth.login('admin', 'Admin@12345').subscribe();

    const req = http.expectOne((r) => r.url.endsWith('/auth/login'));
    expect(req.request.method).toBe('POST');
    req.flush({ access_token: token, token_type: 'bearer', expires_in: 3600, is_admin: true });

    expect(auth.isLoggedIn()).toBeTrue();
    expect(auth.isAdmin()).toBeTrue();
    expect(auth.token()).toBe(token);
  });

  it('a non-admin token does not grant admin', () => {
    const token = fakeJwt({ exp: Math.floor(Date.now() / 1000) + 3600, is_admin: false });
    auth.login('demo', 'Demo@12345').subscribe();
    http.expectOne((r) => r.url.endsWith('/auth/login')).flush({
      access_token: token, token_type: 'bearer', expires_in: 3600, is_admin: false,
    });
    expect(auth.isLoggedIn()).toBeTrue();
    expect(auth.isAdmin()).toBeFalse();
  });
});
