# Game Item Store

A small full-stack digital game-item shop built for the FS SDE technical assignment.
Users log in, browse game items (imported from a CSV), view details, and buy one item per
order to get a receipt.

- **Backend** — Python, **FastAPI**, PostgreSQL, SQLAlchemy 2.0, Alembic, JWT auth.
- **Frontend** — **Angular 17** (standalone components + signals), reactive login form,
  CSS Grid product list, auth guard + HTTP interceptor.

```
game_item_store/
  backend/            # FastAPI API + CSV import + tests   (see backend/README.md)
  frontend/           # Angular SPA                          (see frontend/README.md)
  example/            # sample .csv/.xlsx files for the admin bulk import
  docs/               # assignment PDF, exported OpenAPI is in backend/docs/
  docker-compose.yml  # full stack: db + backend + frontend
  run.sh / run.ps1    # one-command start (Linux/macOS / Windows)
```

## Deviations from the brief

**Purchase request.** The brief asks for one product per request. That request is still
valid and is exactly what the *Buy* button sends:

    POST /api/v1/orders  { "items": [ { "product_id": 13 } ] }

I extended the model so one order can hold several lines (`orders` + `order_items`), which
made a cart possible and matches how a real bill works. Quantity defaults to 1.

**Countries instead of a JO/SA enum.** Locations are rows in a `countries` table, so an
admin can add a country at runtime without a migration or redeploy.

**Per-user country access.** Non-admin users can be limited to certain countries. This is
enforced on the server: an out-of-region product returns 404 (not 403), so the API never
reveals that a product the user may not see exists.

## Run with Docker (one command)

The whole project — PostgreSQL, the FastAPI backend, and the Angular frontend (served by
nginx) — is containerized. With Docker running, use the one-command script:

```bash
./run.sh            # macOS/Linux   (./run.sh fresh = wipe DB & start from scratch)
.\run.ps1           # Windows       (.\run.ps1 fresh = wipe DB & start from scratch)
```

or plain Docker Compose:

```bash
docker compose up --build
```

On first run the backend automatically creates the schema (a single Alembic migration),
seeds the base countries, imports `items.csv`, and creates the users — so everything appears
from scratch with no manual steps.

The compose file reads `JWT_SECRET_KEY` from your environment (or a local `.env`) and falls
back to an obvious development value — set a real secret before any real deployment.

Then open:

- **Frontend** → http://localhost:4200
- **API docs** → http://localhost:8000/docs

Sign in as a regular user with **`demo` / `Demo@12345`**, or as an admin with
**`admin` / `Admin@12345`**. On first start the backend automatically waits for the
database, applies migrations, seeds the base countries (Jordan, Saudi Arabia), imports
`items.csv` (100 products), and creates both users. Stop it with `Ctrl+C`, or
`docker compose down` (add `-v` to also drop the database).

### Admin features

Signing in as **admin** reveals an **Admin** link in the header (`/admin`), where you can:

- **Add countries** at runtime (e.g. UAE) — the product filters update dynamically.
- **Add a single game** via a form.
- **Import games from a file** (`.xlsx` or `.csv`) with columns
  `id, title, description, price, country`. The import is **atomic and fully validated**:
  every cell must be present, `price` must be a valid number, `country` must already exist,
  and no id may be duplicated (in the file or the database). If anything is wrong, **nothing
  is imported** and the response lists either a general problem or the exact **row numbers**
  that failed.
- **Control per-user country access** — under *User access to countries*, give each user an
  "All countries" toggle or tick individual countries. Restricted users only see, open, and
  buy products from their allowed countries; everything is enforced **server-side** (an
  out-of-region product returns 404, not just a hidden button). Admins always see all, and
  the seeded `demo` user starts with all-country access.

> The compose file sets a local-only `JWT_SECRET_KEY`. Generate your own for anything real.

## Quick start (without Docker for the apps)

You need **Python 3.12+**, **Docker** (for PostgreSQL), and **Node.js 18.13+**.

### 1. Backend (terminal 1)

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1            # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

docker compose up -d                     # PostgreSQL on :5432
copy .env.example .env                    # Linux/macOS: cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"   # paste into JWT_SECRET_KEY

alembic upgrade head                      # create tables
python -m scripts.import_products data/items.csv
python -m scripts.create_user demo Demo@12345

uvicorn app.main:app --reload            # http://localhost:8000/docs
```

### 2. Frontend (terminal 2)

```bash
cd frontend
npm install
npm start                                 # http://localhost:4200
```

Open **http://localhost:4200** and sign in with **`demo` / `Demo@12345`**.

## What each part does

| Requirement | Where |
| --- | --- |
| CSV import (idempotent, validated) | `backend/scripts/import_products.py` |
| JWT login, protected endpoints | `backend/app/api/routers/auth.py`, `app/api/deps.py` |
| Paginated product list + JO/SA filter | `backend/app/api/routers/products.py` |
| Product details | `GET /api/v1/products/{id}` |
| Buy → order → receipt | `backend/app/api/routers/orders.py` |
| API docs | Swagger `/docs`, `backend/docs/openapi.json` |
| Login / grid / details / receipt pages | `frontend/src/app/pages/*` |
| Token stored, sent on every request, redirect when logged out | `frontend/src/app/core/auth/*` |

## Design decisions & assumptions

**Database — PostgreSQL** (SQLite in tests): ACID transactions for orders, exact
`NUMERIC(10,2)` money, check constraints (`location` must be JO/SA). Tests run without Docker.

**Backend architecture** — deliberate layers: `router → service → use case → validator +
repository`. Business logic is testable without HTTP; each class has one job.

**Money** — stored as `Decimal`, serialized as JSON **strings** (`"150.00"`) to avoid float
rounding; the frontend just displays the string.

**CSV assumptions** — 100 rows, 10 distinct titles repeated with different prices. **Each row
is its own product** (`id` is unique); duplicates are not merged. **No currency** in the
source data — the plain number is shown; `JO`/`SA` marks the sale location (Jordan / Saudi
Arabia), not a currency. The CSV has no users, so a demo user is seeded by a script. Import
is idempotent (upsert by id); invalid rows are skipped and reported.

**Orders** snapshot the product title/price/location at purchase time, so a receipt stays
correct if the product later changes. One product per order, quantity always 1. Fetching
another user's order returns **404, not 403**, so the API doesn't leak that it exists.

**Auth** — JWT HS256, 60-minute expiry, no refresh token (listed as future work). Same login
error for unknown user and wrong password (no username enumeration). Frontend keeps the token
in `sessionStorage` (simple; production alternative is an `httpOnly` cookie).

**Pagination** — defaults page 1, size 12, max 100. 12 fills a 4- or 2-column grid evenly.

### Payments notes

**Card data.** The app stores no card or payment-instrument data — an order records only
what was bought, at what price, by whom. A real checkout would hand off to a PSP's hosted
page or SDK, so card data never touches this server and PCI-DSS scope stays minimal.

**Retry safety.** `POST /orders` is not idempotent today: a retried request creates a
second order. The next step would be an `Idempotency-Key` header stored with the order, so
a repeat of the same key returns the original order instead of creating a new one.

## Tests

```bash
cd backend && pytest -q               # backend tests (SQLite in-memory, no Docker needed)
cd frontend && ng test --watch=false --browsers=ChromeHeadless   # frontend unit tests
```

The full flow (login → list → details → buy → receipt, plus refresh) has also been verified
end-to-end in the browser against the running backend.

## Stopping services

```bash
docker compose down          # from the repo root; add -v to also delete the database volume
```
