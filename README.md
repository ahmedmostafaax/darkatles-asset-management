# DarkAtlas Asset Management API

A REST API for managing internet-facing assets as part of the DarkAtlas Attack Surface Monitoring (ASM) platform.

## Stack
- Python 3.11 + FastAPI
- PostgreSQL 15
- Docker + Docker Compose
- SQLAlchemy ORM
- Pydantic v2

## Setup & Run

### Prerequisites
- Docker Desktop installed and running

### Run with Docker (one command)
```bash
docker-compose up --build
```

API will be available at: http://localhost:8000

Swagger UI (auto-generated docs): http://localhost:8000/docs

## Environment Variables

Copy `.env.example` to `.env` before running.

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql://postgres:password@db:5432/darkatlas |
| API_KEY | API key for write operations | my-secret-api-key |

## API Endpoints

### Assets
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /assets/ | List assets with filtering & pagination | ❌ |
| GET | /assets/{id} | Get single asset | ❌ |
| POST | /assets/ | Create asset | ✅ |
| PUT | /assets/{id} | Update asset | ✅ |
| DELETE | /assets/{id} | Delete asset | ✅ |
| POST | /assets/bulk-import | Bulk import assets | ✅ |
| PATCH | /assets/{id}/stale | Mark asset as stale | ✅ |

### Relationships
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /relationships/ | Create relationship | ✅ |
| GET | /relationships/asset/{id} | Get asset with its relationships | ❌ |

### Authentication
Add header to all write requests:
