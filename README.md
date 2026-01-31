# CampusOrbit Backend

Production-grade REST API powering the CampusOrbit Education Platform. Built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | FastAPI 0.115+ |
| **Language** | Python 3.11+ |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Database** | PostgreSQL via asyncpg |
| **Migrations** | Alembic |
| **Auth** | JWT (python-jose) + bcrypt (passlib) |
| **Cache** | Redis 5+ |
| **Linting** | Ruff, mypy, pre-commit |
| **Testing** | pytest + pytest-asyncio |

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 5+
- (Optional) Docker & Docker Compose

### 1. Clone & Install

```bash
cd campusorbit-backend
pip install -e ".[dev]"
```

### 2. Start Infrastructure (Docker)

```bash
docker-compose up -d
```

This starts PostgreSQL (port 5432) and Redis (port 6379).

### 3. Configure Environment

Copy `.env.example` to `.env` and update values as needed:

```bash
cp .env.example .env
```

Key variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://campusorbit:campusorbit@localhost:5432/campusorbit_erp` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `JWT_SECRET_KEY` | Secret for JWT token signing | Change in production! |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:3001` |
| `SMTP_HOST` | SMTP server for email notifications | `smtp.gmail.com` |
| `SMTP_USER` / `SMTP_PASS` | SMTP credentials | — |

### 4. Run Migrations

```bash
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

### 5. Seed Demo Data

```bash
python -m app.seed
```

Creates 12 demo users, 5 courses, 10 library books, 6 exams, 12 calendar events, 10 store products, 6 vendors, and much more.

### 6. Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

API docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

---

## Authentication

All endpoints (except `/auth/login`) require a JWT bearer token.

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@campusorbit.edu", "password": "admin123"}'

# Use token
curl http://localhost:8000/api/v1/dashboard/stats \
  -H "Authorization: Bearer <access_token>"
```

### Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@campusorbit.edu` | `admin123` |
| Teacher | `teacher@campusorbit.edu` | `admin123` |
| Student | `student@campusorbit.edu` | `admin123` |
| Parent | `parent@campusorbit.edu` | `admin123` |
| Finance | `finance@campusorbit.edu` | `admin123` |
| Employee | `employee@campusorbit.edu` | `admin123` |

---

## Role-Based Access Control

| Module | Admin | Teacher | Student | Parent | Finance | Employee |
|--------|:-----:|:-------:|:-------:|:------:|:-------:|:--------:|
| Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Users | ✅ | ✅ | — | — | — | ✅ |
| Courses | ✅ | ✅ | ✅ | — | — | — |
| Fees | ✅ | — | ✅ | ✅ | ✅ | — |
| Attendance | ✅ | ✅ | ✅ | ✅ | — | — |
| Library | ✅ | ✅ | ✅ | — | — | — |
| HR & Payroll | ✅ | ✅ | — | — | ✅ | ✅ |
| Expenses | ✅ | — | — | — | ✅ | — |
| Exams | ✅ | ✅ | ✅ | — | — | — |
| Calendar | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Store | ✅ | — | ✅ | ✅ | — | — |
| Vendors | ✅ | — | — | — | — | — |

---

## Development

### Run Tests

```bash
pytest tests/ -v --cov=app
```

### Lint & Format

```bash
ruff check app/ --fix
ruff format app/
mypy app/
```

### Generate Migration

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## Deployment

### Docker

```bash
docker build -t campusorbit-backend .
docker run -p 8000:8000 --env-file .env campusorbit-backend
```

### Production Checklist

- [ ] Change `JWT_SECRET_KEY` to a strong random value
- [ ] Set `APP_ENV=production` and `APP_DEBUG=false`
- [ ] Configure SMTP credentials for email notifications
- [ ] Set proper `CORS_ORIGINS` for your frontend domain
- [ ] Use a managed PostgreSQL instance
- [ ] Set up SSL/TLS
