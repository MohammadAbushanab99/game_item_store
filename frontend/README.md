# Game Item Store — Frontend (Angular)

An Angular 17 single-page app: login, a paginated/filterable product grid, product
details with a Buy button, and a receipt page. Talks to the FastAPI backend.

## Tech stack

- **Angular 17** — standalone components, **signals** for state, new `@if`/`@for` control flow.
- **Reactive forms** for login (same validation rules as the backend).
- **Functional HTTP interceptor + route guard** for auth.
- **SCSS** with CSS Grid; responsive for desktop and mobile.

## Requirements

- **Node.js** (this project was built and verified on **v18.18.0**). The generated project
  targets Angular 17, which supports Node `^18.13.0 || >=20.9.0`.
- The **backend must be running** on `http://localhost:8000` (see `../backend/README.md`).

## Setup & run

```bash
cd frontend
npm install
npm start            # or: npx ng serve  -> http://localhost:4200
```

Open **http://localhost:4200**. You'll be redirected to `/login`.
Demo credentials: **`demo` / `Demo@12345`**

## Configuration

The API base URL lives in `src/environments/environment.ts`:

```ts
export const environment = {
  apiUrl: 'http://localhost:8000/api/v1',
};
```

The backend must allow the dev server origin — its `.env` has
`CORS_ORIGINS=["http://localhost:4200"]`.

## Project structure

```
src/app/
  app.component.*          # shell: header + Logout (shown only when logged in) + <router-outlet>
  app.config.ts           # provideRouter + provideHttpClient(withInterceptors([authInterceptor]))
  app.routes.ts           # lazy routes; /products, /products/:id, /orders/:id are guarded
  core/
    models/api.models.ts   # TypeScript mirror of the backend DTOs
    auth/
      auth.service.ts      # token signal, sessionStorage, JWT expiry check
      auth.interceptor.ts  # adds Bearer header; logs out on 401
      auth.guard.ts        # redirects to /login?returnUrl=... when not logged in
    api/
      product-api.service.ts
      order-api.service.ts
  pages/
    login-page/            # reactive form
    product-list-page/     # CSS Grid, filter, pagination (state kept in the URL)
    product-details-page/  # details + Buy
    receipt-page/          # loads the order from the API (survives refresh)
```

## Design decisions

- **Token in `sessionStorage`** — cleared when the tab closes, expiry checked before every
  request. The most secure production option is an `httpOnly` cookie (JS can't read it);
  `sessionStorage` was chosen to keep the assignment simple. Angular escapes all template
  output, which blocks the XSS that could steal it.
- **State via Angular signals + services** (no NgRx) — right-sized for this scope.
- **Pagination + filter live in the URL** (`?page=2&location=JO`) so refresh and the back
  button work; a fast filter click cancels the in-flight request (`switchMap`).
- **Buy button disables while the request runs**, so a double click can't create two orders.
- **Receipt loads from the API by order id**, not from router state, so a refresh still works.
- **Prices are strings** (`"150.00"`) exactly as the backend sends them — no float rounding.

## Verified end-to-end

Login → guard redirect → product grid (Page 1 of 9) → details → Buy → receipt
(`ORD-...`, COMPLETED) → receipt survives a full page refresh. Production build
(`ng build`) compiles cleanly.
