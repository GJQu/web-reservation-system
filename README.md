# Art Studio Reservation System

A full-stack reservation system for an art studio, built with Flask. Demonstrates backend engineering patterns including RESTful API design, ORM-based data modeling, database migrations, comprehensive testing, and containerized deployment.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Flask, SQLAlchemy, Marshmallow |
| **Database** | SQLite (swappable to PostgreSQL via SQLAlchemy) |
| **Auth** | Flask-Login with Werkzeug password hashing |
| **Testing** | pytest with in-memory SQLite |
| **Infrastructure** | Docker, GitHub Actions CI/CD |
| **Frontend** | Jinja2 templates, Bootstrap 5 |

## Architecture

```
app/
  __init__.py          # Application factory (create_app)
  config.py            # Environment-based configuration
  extensions.py        # SQLAlchemy, Migrate, LoginManager
  models.py            # User, StudioClass, Reservation
  auth/                # Authentication blueprint
  main/                # Public pages blueprint
  reservations/        # Reservation management blueprint
  api/                 # REST API blueprint (/api/v1/)
    schemas.py         # Marshmallow serialization
    errors.py          # Structured error handling
  templates/
  static/
tests/                 # 35 tests (models, auth, API, integration)
migrations/            # Alembic schema versioning
scripts/seed_data.py   # Database seeder
```

**Key patterns:** Application factory for test isolation, Blueprints for separation of concerns, soft deletes with audit timestamps, capacity enforcement with computed properties.

## Quick Start

### Local Development

```bash
make setup                     # Create venv, install deps
FLASK_APP=app flask db upgrade # Apply migrations
python scripts/seed_data.py    # Seed classes + test user
make run                       # Start dev server on :5000
```

### Docker

```bash
docker compose up --build      # Build + run (auto-migrates and seeds)
```

### Testing

```bash
make test                      # Run 35 tests
make lint                      # Ruff lint + format check
```

## REST API

All endpoints under `/api/v1/`. Responses use `{"data": ..., "error": ...}` format.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/classes` | No | List all classes with availability |
| GET | `/api/v1/classes/:id` | No | Get single class detail |
| GET | `/api/v1/reservations` | Yes | List current user's reservations |
| POST | `/api/v1/reservations` | Yes | Create reservation `{"class_id": 1}` |
| DELETE | `/api/v1/reservations/:id` | Yes | Cancel reservation (soft delete) |
| GET | `/api/v1/users/me` | Yes | Current user profile |

**Error codes:** `NOT_FOUND`, `CLASS_FULL`, `DUPLICATE_RESERVATION`, `FORBIDDEN`, `VALIDATION_ERROR`

## Data Model

```
users         classes            reservations
------        --------           -------------
id (PK)       id (PK)            id (PK)
username      name               user_id (FK -> users)
email         day                class_id (FK -> classes)
password_hash start_time         status (confirmed/cancelled)
first_name    end_time           created_at
last_name     capacity           cancelled_at
created_at    created_at
updated_at
```

**Design decisions:**
- Normalized schema: reservation references user via FK (no denormalized name/email copies)
- Soft deletes: cancelled reservations keep history via `status` + `cancelled_at`
- Capacity enforcement: `StudioClass.spots_remaining` computed from active reservation count
- Unique constraint on `(user_id, class_id)` prevents double-booking

## CI/CD

GitHub Actions pipeline runs on push/PR to main:
1. **Lint** - ruff check + format
2. **Test** - pytest (35 tests)
3. **Build** - Docker image build

## Credits

Art portfolio credit: Peiyao Wang

## License

MIT License - see [LICENSE](LICENSE) for details.
