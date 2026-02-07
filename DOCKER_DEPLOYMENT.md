# Docker Deployment Guide

Complete guide for deploying Todo Phase5 application using Docker and Docker Compose.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Build and Run](#build-and-run)
5. [Configuration](#configuration)
6. [Services](#services)
7. [Testing](#testing)
8. [Scaling](#scaling)
9. [Troubleshooting](#troubleshooting)
10. [Production Tips](#production-tips)

---

## Quick Start

### One-Command Deployment

```bash
# Clone repo and navigate to directory
cd todo_phase5

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

**Access the API:**
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## Prerequisites

### Required Software

1. **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
   - Download: https://www.docker.com/products/docker-desktop
   - Minimum version: 20.10+

2. **Docker Compose** (included in Docker Desktop)
   - Minimum version: 2.0+
   - Verify: `docker-compose --version`

### System Requirements

- **RAM**: Minimum 4GB (8GB recommended)
- **Disk**: Minimum 10GB free space
- **CPU**: 2+ cores recommended

---

## Architecture

### Docker Compose Stack

```
┌─────────────────────────────────────────────┐
│         Docker Compose Network              │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Backend  │  │ Backend  │  │ Postgres │ │
│  │  :8000   │  │  :8001   │  │  :5432   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
│       │             │              │        │
│       └─────────┬───┴──────────────┘        │
│                 │                            │
│  ┌──────────┐  │  ┌──────────┐             │
│  │  Redis   │◄─┴─►│  Kafka   │             │
│  │  :6379   │     │  :29092  │             │
│  └──────────┘     └──────────┘             │
└─────────────────────────────────────────────┘
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| **backend** | 8000 | FastAPI application (primary) |
| **backend-replica** | 8001 | FastAPI replica (optional) |
| **postgres** | 5432 | PostgreSQL database |
| **redis** | 6379 | WebSocket scaling |
| **kafka** | 29092 | Event streaming |
| **zookeeper** | 2181 | Kafka coordination |

---

## Build and Run

### Step 1: Create Environment File

```bash
# Copy example
cp .env.example .env

# Edit .env (optional - defaults work for Docker)
# SECRET_KEY will be auto-generated if not set
```

### Step 2: Build Images

```bash
# Build backend image
docker-compose build

# Or build with no cache
docker-compose build --no-cache
```

### Step 3: Start Services

**Start all services (single instance):**
```bash
docker-compose up -d
```

**Start with replica (multi-instance for testing):**
```bash
docker-compose --profile replica up -d
```

**View startup logs:**
```bash
docker-compose logs -f
```

### Step 4: Verify Deployment

**Check all services are running:**
```bash
docker-compose ps
```

Expected output:
```
NAME                  STATUS    PORTS
todo-backend          Up        0.0.0.0:8000->8000/tcp
todo-postgres         Up        0.0.0.0:5432->5432/tcp
todo-redis            Up        0.0.0.0:6379->6379/tcp
todo-kafka            Up        0.0.0.0:29092->29092/tcp
todo-zookeeper        Up        2181/tcp
```

**Test health endpoints:**
```bash
# Backend health
curl http://localhost:8000/health

# Database connection
curl http://localhost:8000/health
# Should return: {"status":"ok","environment":"production"}
```

---

## Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Authentication (REQUIRED in production)
SECRET_KEY=your-super-secret-key-min-32-chars

# Database (auto-configured in docker-compose)
DATABASE_URL=postgresql://todouser:todopass123@postgres:5432/todo_phase5
ENVIRONMENT=production

# Redis (auto-configured)
REDIS_URL=redis://:todoredis123@redis:6379

# Kafka (auto-configured)
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# OpenAI (optional)
# OPENAI_API_KEY=sk-...
```

### Generate Secure SECRET_KEY

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or OpenSSL
openssl rand -base64 32
```

### Docker Compose Overrides

Create `docker-compose.override.yml` for local customizations:

```yaml
version: '3.8'

services:
  backend:
    environment:
      # Override any environment variable
      LOG_LEVEL: DEBUG
    volumes:
      # Mount local code for development
      - ./:/app
```

---

## Services

### PostgreSQL Database

**Access database:**
```bash
docker-compose exec postgres psql -U todouser -d todo_phase5
```

**Common commands:**
```sql
-- List tables
\dt

-- Count users
SELECT COUNT(*) FROM users;

-- Count tasks
SELECT COUNT(*) FROM tasks;

-- Exit
\q
```

**Backup database:**
```bash
docker-compose exec postgres pg_dump -U todouser todo_phase5 > backup.sql
```

**Restore database:**
```bash
cat backup.sql | docker-compose exec -T postgres psql -U todouser todo_phase5
```

### Redis

**Access Redis CLI:**
```bash
docker-compose exec redis redis-cli -a todoredis123
```

**Common commands:**
```bash
# Test connection
127.0.0.1:6379> PING
# Output: PONG

# Check pub/sub channels
127.0.0.1:6379> PUBSUB CHANNELS

# Monitor all commands
127.0.0.1:6379> MONITOR

# Get memory usage
127.0.0.1:6379> INFO memory
```

### Kafka

**List topics:**
```bash
docker-compose exec kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --list
```

**Create topic:**
```bash
docker-compose exec kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create \
  --topic test-topic \
  --partitions 3 \
  --replication-factor 1
```

**Consume messages:**
```bash
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning
```

**Produce test message:**
```bash
docker-compose exec kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic task-events
# Type message and press Enter
```

### Backend Application

**View logs:**
```bash
# All logs
docker-compose logs backend

# Follow logs
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

**Execute commands in backend:**
```bash
# Python shell
docker-compose exec backend python

# Run migration
docker-compose exec backend python migrate_sqlite_to_postgres.py

# Check installed packages
docker-compose exec backend pip list
```

---

## Testing

### API Testing

**Register user:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'

# Save the access_token from response
```

**Create task:**
```bash
TOKEN="your-access-token-here"

curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Docker Test Task",
    "description": "Testing Docker deployment",
    "priority": "high"
  }'
```

**List tasks:**
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN"
```

### WebSocket Testing

Create `test_websocket.html`:

```html
<!DOCTYPE html>
<html>
<head><title>WebSocket Test</title></head>
<body>
  <h1>WebSocket Test</h1>
  <div id="messages"></div>
  <script>
    const token = 'YOUR_JWT_TOKEN';
    const ws = new WebSocket(`ws://localhost:8000/ws/tasks?token=${token}`);

    ws.onopen = () => {
      document.getElementById('messages').innerHTML += '<p>✅ Connected</p>';
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      document.getElementById('messages').innerHTML +=
        `<p>📩 ${data.type}: ${JSON.stringify(data.data)}</p>`;
    };

    ws.onerror = (error) => {
      document.getElementById('messages').innerHTML += '<p>❌ Error</p>';
    };
  </script>
</body>
</html>
```

Open in browser and create tasks via API to see real-time updates.

---

## Scaling

### Multi-Instance Deployment

**Start with replica:**
```bash
docker-compose --profile replica up -d
```

This starts:
- **backend** on port 8000
- **backend-replica** on port 8001
- Both share PostgreSQL, Redis, Kafka

**Test multi-instance:**
```bash
# Create task on instance 1
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "Instance 1 Task"}'

# Create task on instance 2
curl -X POST http://localhost:8001/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "Instance 2 Task"}'

# Both instances can read all tasks
curl http://localhost:8000/api/tasks -H "Authorization: Bearer $TOKEN"
curl http://localhost:8001/api/tasks -H "Authorization: Bearer $TOKEN"
```

**Test Redis WebSocket broadcasting:**
- Connect WebSocket to port 8000
- Connect WebSocket to port 8001
- Create task via either port
- Both WebSocket clients receive the update! ✅

### Manual Scaling

**Scale backend to 3 instances:**
```bash
docker-compose up -d --scale backend=3
```

**Note:** Port mapping conflicts will occur. For production, use a load balancer (nginx, traefik).

---

## Troubleshooting

### Common Issues

#### Issue: Port Already in Use

**Error:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution:**
```bash
# Find process using port
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Kill process or change port in docker-compose.yml
```

#### Issue: Container Keeps Restarting

**Check logs:**
```bash
docker-compose logs backend
```

**Common causes:**
1. Database not ready (health check timeout)
2. Missing environment variable
3. Database connection error

**Solution:**
```bash
# Check if database is ready
docker-compose exec postgres pg_isready -U todouser

# Restart services
docker-compose restart backend
```

#### Issue: Database Connection Failed

**Error:** `could not connect to server: Connection refused`

**Solution:**
```bash
# Check postgres is running
docker-compose ps postgres

# Check postgres logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres

# Wait for health check
docker-compose ps
```

#### Issue: Kafka Not Ready

**Error:** `KafkaError: NoBrokersAvailable`

**Solution:**
```bash
# Kafka takes 30-60s to start
docker-compose logs kafka

# Wait for "started (kafka.server.KafkaServer)"

# Check Kafka health
docker-compose exec kafka kafka-broker-api-versions \
  --bootstrap-server localhost:9092
```

#### Issue: Build Fails

**Solution:**
```bash
# Clean build
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Debugging Commands

```bash
# Check container status
docker-compose ps

# View all logs
docker-compose logs

# View specific service logs
docker-compose logs -f backend

# Execute shell in container
docker-compose exec backend sh

# Check network
docker network inspect todo_phase5_todo-network

# Check volumes
docker volume ls | grep todo
```

---

## Production Tips

### Security

**1. Change all default passwords:**
```yaml
# In docker-compose.yml
postgres:
  environment:
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

redis:
  command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
```

**2. Use secrets file:**
```bash
# Create .env file (not in git)
SECRET_KEY=<generate-strong-key>
POSTGRES_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>
```

**3. Enable SSL/TLS:**
- Use HTTPS reverse proxy (nginx, traefik)
- Configure PostgreSQL SSL
- Use `rediss://` for Redis

### Performance

**1. Increase resources:**
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

**2. Use production-grade images:**
```dockerfile
# In Dockerfile, use uvicorn with workers
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--workers", "4"]
```

**3. Enable connection pooling:**
Already configured in `database.py` for production mode.

### Monitoring

**1. Health checks:**
```bash
# Automated health monitoring
watch -n 5 'docker-compose ps'
```

**2. Resource usage:**
```bash
docker stats
```

**3. Logs to file:**
```bash
docker-compose logs -f > app.log 2>&1 &
```

### Backup Strategy

**Automated backup script:**

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker-compose exec -T postgres pg_dump -U todouser todo_phase5 \
  > $BACKUP_DIR/postgres_$DATE.sql

# Backup Redis
docker-compose exec redis redis-cli -a todoredis123 --rdb /data/dump.rdb
docker cp todo-redis:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

echo "✅ Backup completed: $DATE"
```

**Schedule with cron:**
```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup.sh
```

---

## Commands Reference

### Docker Compose Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart service
docker-compose restart backend

# View logs
docker-compose logs -f

# Build images
docker-compose build

# Pull latest images
docker-compose pull

# Execute command in service
docker-compose exec backend <command>

# Scale service
docker-compose up -d --scale backend=3
```

### Docker Commands

```bash
# List containers
docker ps

# List all containers
docker ps -a

# View container logs
docker logs -f todo-backend

# Execute shell in container
docker exec -it todo-backend sh

# Remove container
docker rm -f todo-backend

# List images
docker images

# Remove image
docker rmi todo_phase5-backend

# System cleanup
docker system prune -a
```

---

## Next Steps

1. ✅ Deploy with Docker Compose
2. ✅ Test all services
3. ✅ Configure environment variables
4. 🔄 Add nginx reverse proxy
5. 🔄 Set up SSL/TLS certificates
6. 🔄 Configure CI/CD pipeline
7. 🔄 Deploy to production server

---

**Docker deployment complete! Your Todo Phase5 application is running with PostgreSQL, Redis, and Kafka. 🐳🎉**
