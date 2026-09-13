# Game Item Store — Backend API

A FastAPI service that imports digital game items from a CSV, authenticates users with
JWT, lists products (paginated, filterable by location), shows product details, and lets a
user buy one item per order and retrieve the receipt.

## Tech stack & rationale

| Choice | Why |
| --- | --- |
| **FastAPI** | Typed request/response models, dependency injection (`Depends`), and OpenAPI/Swagger generated automatically at `/docs` — covers the "API documentation" requirement out of the box. |
| **PostgreSQL** | ACID transactions (an order is fully saved or not at all), `NUMERIC(10,2)` stores money exactly (no float rounding), foreign keys + check constraints protect data (`location` must be `JO`/`SA`). Runs with one Docker command. |
| **SQLAlchemy 2.0 + Alembic** | Typed ORM models (like JPA entities) and versioned migrations (like Flyway). |
| **Decimal for money** | Prices are `Decimal` in Python and serialized as JSON **strings** (e.g. `"150.00"`) so there is never float rounding. |
| **SQLite in-memory for tests** | Tests run without Docker. |

The code uses a deliberate layered / clean-architecture style:
`router → service → use case → validator + repository`. Business logic lives in use cases,
so it can be unit-tested without HTTP, and each class has one job.

## Project layout

```
backend/
  app/
    main.py                # FastAPI app: CORS, error handlers, routers
    core/                  # config, database, security (JWT/bcrypt), exceptions, error_handlers
    models/                # SQLAlchemy entities: product, user, order, enums
    schemas/               # Pydantic DTOs: auth, product, order, common
    repositories/          # data access (JpaRepository equivalents)
    validators/            # business-rule validators
    use_cases/             # one class per action, method execute()
    services/              # per-domain facades the routers call
    api/
      deps.py              # dependency wiring + get_current_user
      routers/             # auth.py, products.py, orders.py
  alembic/                 # migrations
  scripts/                 # import_products.py, create_user.py
  tests/                   # conftest.py, test_api.py (11 tests, SQLite in-memory)
  data/items.csv           # source data
  docs/openapi.json        # exported OpenAPI contract
  requirements.txt
  .env.example
```

> The database runs from the **root** `docker-compose.yml` (`db` service). To run the whole
> stack in Docker instead, use `./run.sh` / `.\run.ps1` from the repo root.

## Setup & run (about 5 minutes)

All commands are run from inside `backend/`.

```powershell
# 1. Virtual env + dependencies
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

# 2. Start PostgreSQL (from the repo root — starts just the db service)
docker compose up -d db                # Postgres 17 on localhost:5432

# 3. Configure environment
copy .env.example .env                 # Linux/macOS: cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"   # paste into JWT_SECRET_KEY in .env

# 4. Create the tables
alembic upgrade head

# 5. Load data + create a login user
python -m scripts.import_products data/items.csv
python -m scripts.create_user demo Demo@12345

# 6. Run the API
uvicorn app.main:app --reload          # http://localhost:8000/docs
```

Demo credentials: **`demo` / `Demo@12345`**

## API contract

Base URL `http://localhost:8000/api/v1`. Everything except `login` and `/health` needs
`Authorization: Bearer <token>`.

| Endpoint | Input | Success | Errors |
| --- | --- | --- | --- |
| `POST /auth/login` | body `{username, password}` | `200 {access_token, token_type, expires_in}` | `400` invalid body · `401` wrong credentials |
| `GET /products` | query `page=1`, `size=12` (1–100), `location=JO\|SA` | `200 {items, page, size, total_items, total_pages}` | `400` bad query · `401` |
| `GET /products/{id}` | path `id > 0` | `200` product | `401` · `404` |
| `POST /orders` | body `{product_id}` | `201` order (receipt data) | `400` · `401` · `404` · `422` cannot be bought |
| `GET /orders/{id}` | path `id` | `200` order | `401` · `404` (also for other users' orders) |
| `GET /countries` | — | `200` list of `{code, name}` | `401` |
| `POST /countries` | body `{code, name}` | `201` country | `400` · `401` · `403` (admin only) |
| `POST /products` | body `{title, description, price, location, id?}` | `201` product | `400` · `401` · `403` (admin only) |
| `POST /products/import` | multipart `file` (`.xlsx`/`.csv`) | `200 {inserted, message}` | `400` (per-row details) · `401` · `403` (admin only) |
| `GET /health` | — | `200 {status: "ok"}` | — |

**Roles**: `POST /countries`, `POST /products`, and `POST /products/import` require an admin
token (seeded user `admin` / `Admin@12345`); non-admins get `403 FORBIDDEN`. The login
response and JWT include an `is_admin` flag.

**Import validation**: the file needs columns `id, title, description, price, country`. It is
validated atomically — every cell must be present, `price` a valid number (≥ 0, ≤ 2 decimals),
`country` an existing code, and no duplicate id (in the file or DB). On any error nothing is
inserted and the response's `details` list the failing **row numbers** (or a single general
message for problems like a missing column).

Interactive docs: **`/docs`** (Swagger UI) and **`/redoc`**. The contract is also exported to
`docs/openapi.json`.

### Every error has the same shape

```json
{ "error": { "code": "VALIDATION_ERROR", "message": "Invalid request", "details": [
  { "field": "page", "message": "Input should be greater than or equal to 1" }
] } }
```

### Example calls

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"Demo@12345"}'

curl "http://localhost:8000/api/v1/products?page=1&size=12&location=JO" \
  -H "Authorization: Bearer <token>"

curl -X POST http://localhost:8000/api/v1/orders \
  -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"product_id": 13}'
```

## Tests

```powershell
pytest -v          # 11 tests, SQLite in-memory (no Docker needed)
```

Covers: login success/failure, validation errors, token-protected endpoints, default
pagination, location filter, invalid params, product 404, purchase + receipt, purchase
business rules, and order-ownership isolation.

## CSV import notes / assumptions

- **`items.csv` has 100 rows, 5 columns** (`id, title, description, price, location`), no empty cells.
- Only 10 distinct titles, each repeated 10× with slightly different prices. **Each row is
  treated as its own product** (`id` is unique) — duplicates are *not* merged.
- 4 prices have decimals (`20.5`, `75.5`, `60.5`, `110.5`) → stored as `NUMERIC(10,2)`,
  handled as `Decimal`, never `float`.
- **No currency** in the source data; the plain number is shown. `JO`/`SA` only marks where
  the item is sold (Jordan / Saudi Arabia).
- The import is **idempotent**: rows are upserted by `id` (`db.merge`), so running it twice
  imports 100 both times and creates no duplicates. Bad rows are validated, skipped, and
  reported (they do not abort the import).
- The CSV has no users, so `scripts.create_user` seeds a demo login.

## Design decisions

- **Order snapshots** the product title, price and location at purchase time, so a receipt
  always shows what the user paid even if the product price later changes.
- **Passwords** are bcrypt-hashed; login returns the same message for "unknown user" and
  "wrong password" so usernames can't be enumerated.
- **JWT** tokens expire (default 60 min); a `get_current_user` dependency validates the
  Bearer token on every protected route.
- Fetching another user's order returns **404, not 403**, so the API doesn't leak that the
  order exists.
