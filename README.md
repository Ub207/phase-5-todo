---
title: Todo Phase 5
emoji: ✅
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Todo Phase 5 - Event-Driven Task Management System

A production-ready FastAPI backend with Kafka event streaming, WebSocket real-time updates, and Kubernetes deployment.

## 🚀 Features

### Core Functionality
- ✅ **User Authentication** - JWT-based auth with bcrypt password hashing
- ✅ **Task Management** - CRUD operations with priority levels
- ✅ **Recurring Tasks** - Flexible scheduling (daily, weekly, monthly, custom)
- ✅ **Real-Time Updates** - WebSocket support for instant UI updates
- ✅ **Event-Driven Architecture** - Kafka integration for scalable event processing

### Production Features
- ✅ **Database Options** - SQLite (dev) or PostgreSQL (production)
- ✅ **Kafka Integration** - Producer/consumer with idempotent processing
- ✅ **WebSocket Manager** - User-specific broadcasting with JWT auth
- ✅ **Kubernetes Ready** - Helm charts, HPA, and health probes
- ✅ **Docker Support** - Multi-stage builds with security hardening
- ✅ **Connection Pooling** - Optimized for production workloads

## 📋 Prerequisites

- **Python 3.8+** - Backend runtime
- **Node.js 18+** - Frontend (optional)
- **PostgreSQL 15+** - Production database (optional for dev)
- **Kafka** - Event streaming (optional for dev)
- **Docker** - Containerization (optional)

## 🏃 Quick Start

### 1. Install Dependencies

```bash
# Backend dependencies (includes Kafka and PostgreSQL)
pip install -r requirements_kafka.txt
```

### 2. Configure Environment

**Development (SQLite):**
```bash
cp .env.example .env
# Edit .env - SQLite is used by default when DATABASE_URL is not set
```

**Production (PostgreSQL):**
```bash
cp .env.example .env
# Edit .env and set:
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@localhost:5432/todo_phase5
```

### 3. Start the Backend

```bash
# Development mode (SQLite)
uvicorn main:app --reload

# Production mode (PostgreSQL)
ENVIRONMENT=production uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Access the API

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **WebSocket Stats**: http://localhost:8000/ws/stats

## 📚 Documentation

### Core Guides
- **[PostgreSQL Migration](POSTGRESQL_MIGRATION.md)** - Complete guide for migrating from SQLite
- **[Kafka Integration](KAFKA_INTEGRATION_GUIDE.md)** - Event streaming setup
- **[Event System](EVENTS.md)** - Event-driven architecture overview
- **[Phase 5 Implementation](PHASE5_IMPLEMENTATION.md)** - Feature summary
- **[Quick Start](QUICK_START.md)** - Get running in 3 commands

### Deployment
- **[Kubernetes Guide](kubernetes/DEPLOYMENT_GUIDE.md)** - Production deployment
- **[Helm Charts](helm/todo-phase5/)** - Kubernetes packaging
- **[Docker Guide](Dockerfile)** - Container builds

## 🗄️ Database Setup

### SQLite (Development)

**Default - No setup required:**
```bash
# Automatically uses ./todo.db
uvicorn main:app --reload
```

### PostgreSQL (Production)

**Option 1: Docker (Recommended for local testing)**
```bash
docker run -d \
  --name postgres-todo \
  -e POSTGRES_USER=todouser \
  -e POSTGRES_PASSWORD=todopass123 \
  -e POSTGRES_DB=todo_phase5 \
  -p 5432:5432 \
  postgres:15-alpine
```

**Option 2: Local Installation**
- [PostgreSQL Downloads](https://www.postgresql.org/download/)

**Migrate from SQLite:**
```bash
# Set PostgreSQL URL
export DATABASE_URL="postgresql://todouser:todopass123@localhost:5432/todo_phase5"

# Run migration script
python migrate_sqlite_to_postgres.py

# Start backend
uvicorn main:app --reload
```

See **[POSTGRESQL_MIGRATION.md](POSTGRESQL_MIGRATION.md)** for complete guide.

## 🌐 Environment Variables

```bash
# Environment type: development, production, serverless
ENVIRONMENT=development

# Database (leave empty for SQLite)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Kafka (optional)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

See `.env.example` for complete configuration options.

## 🧪 Testing

### Run Event System Tests
```bash
python test_events.py
```

### Run Kafka Integration Tests
```bash
# Ensure Kafka is running first
python test_kafka_integration.py
```

### Run API Tests
```bash
python test_api.py
```

### Run Advanced Features Tests
```bash
python test_advanced_features.py
```

## 🏗️ Project Structure

```
todo_phase5/
├── main.py                    # FastAPI application entry point
├── database.py                # Database configuration (SQLite/PostgreSQL)
├── models.py                  # SQLAlchemy ORM models
├── schemas.py                 # Pydantic schemas for validation
├── auth_utils.py              # Authentication utilities
│
├── routers/                   # API route handlers
│   ├── tasks.py              # Task CRUD endpoints
│   ├── recurring.py          # Recurring task endpoints
│   └── websocket_router.py   # WebSocket endpoints
│
├── events.py                  # Event bus implementation
├── event_handlers.py          # Event listeners
├── kafka_service.py           # Kafka consumer service
├── websocket_manager.py       # WebSocket connection manager
│
├── migrate_*.py               # Database migration scripts
├── test_*.py                  # Test suites
│
├── kubernetes/                # Kubernetes manifests
│   ├── postgres/             # PostgreSQL deployment
│   ├── kafka/                # Kafka cluster (Strimzi)
│   └── dapr/                 # Dapr components
│
├── helm/                      # Helm charts
│   └── todo-phase5/          # Application chart
│
├── frontend/                  # Next.js frontend
│   ├── app/                  # App router pages
│   ├── components/           # React components
│   └── lib/                  # API client
│
└── docs/                      # Documentation (*.md files)
```

## 🚢 Deployment

### Local Development
```bash
uvicorn main:app --reload
```

### Docker
```bash
# Build image
docker build -t todo-phase5-backend:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  todo-phase5-backend:latest
```

### Kubernetes (Production)
```bash
# Quick deploy with script
./kubernetes/deploy.ps1 -DeployAll

# Or manual Helm deployment
helm install todo-phase5-app helm/todo-phase5 -n todo-phase5
```

See **[kubernetes/DEPLOYMENT_GUIDE.md](kubernetes/DEPLOYMENT_GUIDE.md)** for complete instructions.

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - Get JWT token

### Tasks
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `POST /api/tasks/{id}/complete` - Mark as complete

### Recurring Tasks
- `GET /api/recurring` - List recurring patterns
- `POST /api/recurring` - Create recurring pattern
- `PUT /api/recurring/{id}` - Update pattern
- `DELETE /api/recurring/{id}` - Delete pattern

### WebSocket
- `WS /ws/tasks?token={jwt}` - Real-time task updates

## 📊 Architecture

```
┌─────────────┐
│  Frontend   │ (Next.js)
└──────┬──────┘
       │ HTTP API / WebSocket
       ▼
┌─────────────────────────────────┐
│      FastAPI Backend            │
│  ┌────────────┐  ┌────────────┐ │
│  │   API      │  │  Kafka     │ │
│  │ Endpoints  │  │ Consumer   │ │
│  └──────┬─────┘  └──────┬─────┘ │
│         │                │       │
│         ▼                ▼       │
│  ┌─────────────────────────┐    │
│  │ PostgreSQL / SQLite     │    │
│  └─────────────────────────┘    │
└─────────────────────────────────┘
         ▲
         │ Events
         │
┌────────┴────────┐
│  Kafka Broker   │
└─────────────────┘
```

## 🔐 Security Features

- ✅ JWT authentication with bcrypt password hashing
- ✅ Non-root containers in Docker
- ✅ Security contexts in Kubernetes
- ✅ Connection pooling with health checks
- ✅ CORS configuration
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Environment-based secrets management

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is part of the Todo Phase5 application.

## 🆘 Support

**Common Issues:**
- [PostgreSQL Connection](POSTGRESQL_MIGRATION.md#troubleshooting)
- [Kafka Setup](KAFKA_INTEGRATION_GUIDE.md#troubleshooting)
- [Kubernetes Deployment](kubernetes/DEPLOYMENT_GUIDE.md#troubleshooting)

**Quick Commands:**
```bash
# Check database connection
python -c "from database import engine; print(engine.url)"

# Test PostgreSQL
psql -U todouser -d todo_phase5 -h localhost

# Check Kafka
python test_kafka_integration.py

# View logs
tail -f /var/log/todo-phase5.log
```

---

**Built with FastAPI, PostgreSQL, Kafka, and Kubernetes for production-scale task management. 🚀**
