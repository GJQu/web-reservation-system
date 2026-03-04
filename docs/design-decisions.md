# Design Decisions & System Design Notes

This document explains the *why* behind each design choice in the reservation system redesign. Use it to review concepts and prepare for system design discussions.

---

## 1. Application Factory Pattern

**What we did:** Replaced the global `app = Flask(__name__)` with a `create_app(config_name)` function in `app/__init__.py`.

**Why it matters:**
- **Test isolation:** Each test creates a fresh app instance with its own in-memory database. Tests don't pollute each other's state.
- **Environment configuration:** One codebase, multiple configs. `create_app("testing")` uses in-memory SQLite, `create_app("production")` reads `DATABASE_URL` from the environment.
- **Circular import prevention:** Extensions (db, migrate, login_manager) are instantiated in `extensions.py` without an app, then initialized inside `create_app()`. This breaks the common Flask circular import problem.

**Interview talking point:** "The application factory pattern is a form of dependency injection — the app's configuration is injected at creation time rather than hardcoded globally. This enables testing with isolated databases and makes the app 12-factor compliant."

**Before:**
```python
app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
db = SQL("sqlite:///reservation.db")
```

**After:**
```python
def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    ...
    return app
```

---

## 2. Blueprint-Based Route Organization

**What we did:** Split routes from one 220-line `app.py` into 4 Blueprints: `auth`, `main`, `reservations`, `api`.

**Why it matters:**
- **Separation of concerns:** Each blueprint owns a domain. Auth logic doesn't mix with reservation logic.
- **Independent development:** In a team, different developers can work on different blueprints without merge conflicts.
- **URL namespacing:** `url_for('auth.login')` vs `url_for('reservations.make_reservation')` makes the code self-documenting about which domain a route belongs to.
- **Selective registration:** You could register only certain blueprints (e.g., skip the web blueprints and deploy API-only).

**Design choice — flat templates vs per-blueprint templates:** We kept templates in a single `app/templates/` directory rather than `auth/templates/auth/`. With only 10 templates, per-blueprint folders add directory nesting without meaningful benefit. In a larger app with 50+ templates, per-blueprint folders would make more sense.

---

## 3. Database Normalization (Fixing the Schema)

**What we did:** Removed `first_name`, `last_name`, `email` from the `reservations` table. Reservations now reference the `users` table via `user_id` FK.

**Why it matters — the original problem:**
The original schema duplicated user data into every reservation:
```sql
-- Old: reservations had first_name, last_name, email (copies of user data)
INSERT INTO reservations (user_id, class_id, first_name, last_name, email) ...
```

This is **denormalization** — the same data exists in two places. Problems:
1. **Update anomaly:** If a user changes their email, old reservations still have the stale email.
2. **Insert anomaly:** The registration route collected first_name/last_name but never saved them to the users table (a bug).
3. **Wasted space:** Same strings stored N times.

**After normalization:**
```sql
-- New: reservation only stores the FK relationship
INSERT INTO reservations (user_id, class_id) ...
-- User info accessed via: reservation.user.first_name
```

**When denormalization IS appropriate:** If you need to snapshot data at the time of the event (e.g., order history should store the price at time of purchase, not the current price). For reservations, we always want the current user data, so normalization is correct.

**Interview talking point:** "I identified a denormalization issue where user data was copied into reservations. This caused an update anomaly — if a user changed their email, reservations would be stale. I normalized to third normal form by using a foreign key relationship. If this were an e-commerce order system, I might keep denormalized data for audit purposes."

---

## 4. Soft Deletes vs Hard Deletes

**What we did:** Instead of `DELETE FROM reservations WHERE id = ?`, we set `status = 'cancelled'` and `cancelled_at = timestamp`.

**Why it matters:**
- **Audit trail:** You can answer "how many reservations were cancelled last month?" and "which users cancel the most?" — impossible with hard deletes.
- **Undo capability:** A soft-deleted reservation can be restored by setting status back to "confirmed."
- **Data pipeline friendly:** ETL pipelines and analytics need historical data. Hard deletes create gaps.
- **Referential integrity:** Other tables or logs referencing a reservation ID won't have dangling references.

**Tradeoff:** Queries must now filter by `status = 'confirmed'` everywhere. We handled this by using `spots_remaining` as a computed property that only counts confirmed reservations:
```python
@property
def spots_remaining(self):
    active = self.reservations.filter_by(status="confirmed").count()
    return self.capacity - active
```

**Interview talking point:** "I chose soft deletes for reservations because the data has analytical value. In a data engineering context, hard deletes are problematic for ETL pipelines — you lose history. The tradeoff is that every query needs to filter on status, but computed properties encapsulate that logic."

---

## 5. REST API Design

**What we did:** Added 6 JSON endpoints under `/api/v1/` alongside the existing web (HTML) routes.

**Key decisions:**

### API Versioning via URL Prefix
We use `/api/v1/classes` rather than header-based versioning (`Accept: application/vnd.api.v1+json`). URL versioning is more visible, easier to debug, and simpler to route. Header versioning is more "pure" REST but harder to test with `curl`.

### Consistent Response Envelope
Every response follows:
```json
{"data": {...}, "error": null}       // success
{"data": null, "error": {"code": "CLASS_FULL", "message": "..."}}  // error
```
This makes client-side parsing predictable — always check `error` first.

### Resource-Oriented URLs
```
GET    /api/v1/classes          # collection
GET    /api/v1/classes/1        # single resource
POST   /api/v1/reservations     # create
DELETE /api/v1/reservations/1   # cancel (soft delete)
```
Nouns for resources, HTTP verbs for actions. `DELETE` maps naturally to "cancel" for reservations.

### Separation of Web and API
The web routes (`/make_reservation`) render HTML templates. The API routes (`/api/v1/reservations`) return JSON. They share the same models and business logic but have different interfaces. This means:
- A mobile app could use the API without the web templates
- The web frontend could be replaced with React/Vue consuming the API
- Each interface can evolve independently

**Interview talking point:** "I separated the API from the web routes using Flask Blueprints. The API uses marshmallow for input validation and serialization, returns consistent JSON envelopes, and uses proper HTTP status codes (201 Created, 409 Conflict for capacity/duplicate errors). The web routes share the same model layer but render HTML."

---

## 6. Marshmallow for Serialization/Validation

**What we did:** Created schema classes that validate incoming JSON and serialize model objects to JSON.

**Why not just `model.__dict__` or `jsonify()`?**
- **Security:** Without a schema, you might accidentally expose `password_hash` in the user endpoint.
- **Validation:** `ReservationCreateSchema` ensures `class_id` is present and is an integer before hitting the database.
- **Transformation:** Schemas can format fields (e.g., time format `"%I:%M %p"`) and compute derived fields (`spots_remaining`).
- **Documentation:** Schema definitions serve as a contract for what the API accepts and returns.

```python
class ReservationCreateSchema(Schema):
    class_id = fields.Int(required=True)  # Only field needed — user comes from session
```

Notice that the create schema only needs `class_id`. The old web form asked for name and email on every reservation — but you're already logged in, so that data comes from the user session. This is a security improvement (users can't make reservations under someone else's name).

---

## 7. Custom Error Hierarchy

**What we did:** Created `APIError` base class with specific subclasses:
- `ClassFullError` (409 Conflict)
- `DuplicateReservationError` (409 Conflict)
- `NotFoundError` (404)
- `ForbiddenError` (403)

**Why it matters:**
- **Consistent error format:** The error handler on the API blueprint catches all `APIError` instances and formats them identically.
- **Specific error codes:** Clients can programmatically handle `CLASS_FULL` differently from `DUPLICATE_RESERVATION` (e.g., show different UI messages).
- **HTTP semantics:** 409 Conflict for business rule violations (class full, duplicate booking) vs 404 for missing resources vs 403 for authorization.

**Design choice — why 409 instead of 400 for "class full"?**
400 means "your request was malformed." But the request was perfectly valid JSON — the problem is the current state of the resource (class is at capacity). 409 Conflict means "your request conflicts with the current state," which is semantically precise.

---

## 8. Capacity Enforcement as a Computed Property

**What we did:**
```python
class StudioClass(db.Model):
    capacity = db.Column(db.Integer, default=10)

    @property
    def spots_remaining(self):
        active = self.reservations.filter_by(status="confirmed").count()
        return self.capacity - active
```

**Why a property instead of a stored column?**
- A stored `spots_remaining` column would need to be decremented on every reservation and incremented on every cancellation. This creates race conditions under concurrent access (two people book the last spot simultaneously).
- The property queries the actual count each time, which is always accurate.
- For our scale (art studio, ~10 classes, ~100 reservations), the per-request COUNT query is negligible.

**At scale, what would change?** If this were a concert ticketing system with millions of concurrent users:
- Use database-level locking (`SELECT ... FOR UPDATE`) or optimistic locking (version column)
- Consider a separate counter cache with atomic operations (Redis `DECR`)
- The computed property approach doesn't scale, but it's correct for our use case

**Interview talking point:** "I used a computed property for availability because it avoids race conditions from maintaining a separate counter. At our scale, the COUNT query per request is fine. For high-concurrency scenarios like ticketing, I'd use database-level row locking or an atomic counter in Redis."

---

## 9. Testing Strategy

**What we did:** 35 tests across 4 test files using pytest.

### Test Pyramid
```
         /\
        /  \
       / E2E\        (0 — not needed for portfolio)
      /------\
     / Integr-\      (5 web form tests)
    /  ation   \
   /------------\
  /  API tests   \    (12 endpoint tests)
 /----------------\
/   Model (unit)   \  (9 model tests)
\   Auth (unit)    /  (9 auth tests)
 \________________/
```

### Key Fixture: Application Factory + In-Memory SQLite
```python
@pytest.fixture
def app():
    app = create_app("testing")  # Uses sqlite:///:memory:
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()
```

Each test gets a brand-new database. No test can affect another. This is the payoff of the application factory pattern — without it, you'd need to manually reset the database between tests.

### What the tests cover:
- **Models:** Password hashing, capacity calculation, soft delete semantics, relationship navigation
- **Auth:** Registration (success, duplicate, validation), login (success, wrong password), protected route redirect
- **API:** All 6 endpoints, error cases (capacity, duplicate, forbidden, not found), auth requirements
- **Integration:** Web form submission, cancellation flow, user isolation

**Interview talking point:** "The application factory pattern enables test isolation — each test gets a fresh in-memory SQLite database. I structured tests along the test pyramid: unit tests for models, route tests for auth, endpoint tests for the API, and a few integration tests for the full web flow."

---

## 10. Docker & CI/CD

### Dockerfile Design
```dockerfile
FROM python:3.11-slim       # Slim image (not full, not alpine)
COPY requirements.txt .     # Layer caching: deps change less often than code
RUN pip install ...
COPY . .                    # Code layer rebuilds on every change
CMD ["gunicorn", ...]       # Production WSGI server, not Flask dev server
```

**Why `python:3.11-slim` instead of `python:3.11`?** The full image includes compilers, headers, and tools we don't need at runtime. Slim saves ~600MB of image size. We don't use `alpine` because Alpine uses musl libc, which can cause issues with Python packages that expect glibc.

**Why gunicorn?** Flask's built-in server is single-threaded and not designed for production. Gunicorn runs multiple worker processes to handle concurrent requests.

### CI Pipeline
```
push to main ─── lint (ruff) ──┐
                                ├─ build (docker)
PR to main ──── test (pytest) ─┘
```

Lint and test run in parallel. Build only runs after both pass. This catches:
- Style/formatting issues (lint)
- Broken functionality (test)
- Broken Docker build (build)

**Interview talking point:** "The Dockerfile uses multi-layer caching — dependencies are installed before copying code, so code changes don't trigger a full pip install. The CI pipeline runs lint and tests in parallel, and the Docker build only runs after both pass."

---

## 11. Configuration Strategy (12-Factor App)

**What we did:** Environment-based configuration via `app/config.py` with three config classes.

**12-Factor App Principle III: "Store config in the environment"**

The same code runs in dev, test, and production — only the config changes:
```python
class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///dev.db")

class TestingConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")  # Required
```

**Why not just `if __name__ == "__main__": app.config[...] = ...`?**
Class-based config is:
- **Composable:** `ProductionConfig` can inherit from `Config` and override specific values.
- **Testable:** Tests import `TestingConfig` directly.
- **Secure:** Production secrets come from environment variables, never hardcoded.

---

## 12. Why Flask Instead of FastAPI

**Decision:** Stay with Flask.

**Arguments for FastAPI:**
- Native async support
- Built-in Pydantic validation
- Auto-generated OpenAPI/Swagger docs
- Modern, growing ecosystem

**Arguments for Flask (our choice):**
- Already the existing stack — rewriting costs 2-3 days of translation work
- Flask demonstrates the same backend concepts (blueprints = routers, marshmallow = Pydantic, etc.)
- The design patterns are framework-agnostic — interviewers care about architecture, not the framework name
- Time better spent on data modeling, testing, and infrastructure

**Interview answer:** "I kept Flask because the existing codebase was Flask, and my time was better spent on architecture improvements — ORM integration, migrations, API design, testing, and Docker — than on framework translation. I'm familiar with FastAPI and its async/Pydantic advantages; the patterns I used (factory pattern, blueprints, schema validation) map directly to FastAPI equivalents."

---

## Summary: What Changed and Why

| Before | After | Why |
|--------|-------|-----|
| Single `app.py` (220 lines) | 4 blueprints in `app/` package | Separation of concerns, testability |
| CS50 SQL + raw sqlite3 | SQLAlchemy ORM | Standard tooling, relationships, migrations |
| No migrations | Alembic via Flask-Migrate | Schema versioning, team collaboration |
| Password stored, name/email dropped | Proper registration + Flask-Login | Bug fix, standard auth library |
| Denormalized reservations | Normalized with FK to users | Eliminated update anomalies |
| Hard deletes | Soft deletes with status + timestamp | Audit trail, analytics, undo capability |
| No capacity checking | Computed `spots_remaining` property | Business rule enforcement |
| No API | REST API under `/api/v1/` | Mobile/SPA client support, separation |
| No validation | Marshmallow schemas | Input safety, consistent serialization |
| No tests | 35 pytest tests | Confidence, regression prevention |
| No Docker | Dockerfile + docker-compose | Reproducible environments |
| No CI | GitHub Actions (lint/test/build) | Automated quality gates |
| Hardcoded config | Environment-based config classes | 12-factor compliance |
