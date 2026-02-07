# PostgreSQL Migration Guide

Complete guide for migrating from SQLite to PostgreSQL for production deployment.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Detailed Setup](#detailed-setup)
5. [Migration Process](#migration-process)
6. [Verification](#verification)
7. [Rollback](#rollback)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### Why PostgreSQL?

**SQLite Limitations:**
- Single-file database, not ideal for concurrent writes
- Limited scalability for production workloads
- No network access (local file only)
- Not suitable for Kubernetes/Docker deployments

**PostgreSQL Benefits:**
- Production-grade RDBMS with ACID compliance
- Excellent concurrency and performance
- Built-in replication and high availability
- Industry standard for web applications
- Works seamlessly in Kubernetes/cloud environments

### Architecture Changes

**Before (Development):**
```
FastAPI → SQLite (todo.db)
```

**After (Production):**
```
FastAPI → PostgreSQL (Network DB)
          ├── Connection Pooling (20 connections)
          ├── Health Checks (pool_pre_ping)
          └── Connection Recycling (1 hour)
```

---

## Prerequisites

### Local Development

1. **PostgreSQL Server** (Choose one):
   - **Docker** (Recommended):
     ```bash
     docker run -d \
       --name postgres-todo \
       -e POSTGRES_USER=todouser \
       -e POSTGRES_PASSWORD=todopass123 \
       -e POSTGRES_DB=todo_phase5 \
       -p 5432:5432 \
       postgres:15-alpine
     ```

   - **Windows**:
     - Download from [postgresql.org](https://www.postgresql.org/download/windows/)
     - Install with pgAdmin included

   - **macOS** (Homebrew):
     ```bash
     brew install postgresql@15
     brew services start postgresql@15
     ```

   - **Linux** (Ubuntu/Debian):
     ```bash
     sudo apt update
     sudo apt install postgresql postgresql-contrib
     sudo systemctl start postgresql
     ```

2. **Python Dependencies**:
   ```bash
   pip install -r requirements_kafka.txt
   ```

   This includes:
   - `psycopg2-binary` - PostgreSQL adapter (sync)
   - `asyncpg` - PostgreSQL adapter (async, for future use)
   - `sqlalchemy` - ORM

### Cloud/Production

**Option 1: Kubernetes (Recommended)**
- PostgreSQL deployed via Helm chart (already configured)
- See `kubernetes/postgres/` directory

**Option 2: Managed Services**
- [Neon](https://neon.tech) - Serverless PostgreSQL (Free tier)
- [Supabase](https://supabase.com) - PostgreSQL + Backend (Free tier)
- [Railway](https://railway.app) - Quick deployment
- [Render](https://render.com) - Free PostgreSQL database
- AWS RDS, Google Cloud SQL, Azure Database

---

## Quick Start

### 1. Start PostgreSQL

**Using Docker:**
```bash
docker run -d \
  --name postgres-todo \
  -e POSTGRES_USER=todouser \
  -e POSTGRES_PASSWORD=todopass123 \
  -e POSTGRES_DB=todo_phase5 \
  -p 5432:5432 \
  postgres:15-alpine
```

**Verify it's running:**
```bash
docker ps | grep postgres-todo
# Or check port
netstat -an | findstr 5432  # Windows
netstat -an | grep 5432     # Linux/Mac
```

### 2. Configure Environment

Create `.env` file:
```bash
# Copy example
cp .env.example .env
```

Edit `.env`:
```bash
# Set environment type
ENVIRONMENT=production

# Set database URL
DATABASE_URL=postgresql://todouser:todopass123@localhost:5432/todo_phase5

# Keep existing auth settings
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

### 3. Run Migration

**Dry run first (recommended):**
```bash
python migrate_sqlite_to_postgres.py --dry-run
```

Expected output:
```
🚀 SQLITE TO POSTGRESQL MIGRATION
🔍 Running in DRY RUN mode (no changes will be made)

📡 Connecting to databases...
✅ SQLite: sqlite:///./todo.db
✅ PostgreSQL: localhost:5432/todo_phase5

🔍 Analyzing SQLite database...
   Tables found: users, tasks, recurring_patterns

   📊 Data Summary:
      Users: 5
      Tasks: 23
      Recurring Patterns: 3

[DRY RUN] Would create tables: users, tasks, recurring_patterns
[DRY RUN] Would migrate 5 users
[DRY RUN] Would migrate 23 tasks
[DRY RUN] Would migrate 3 recurring patterns

📊 MIGRATION SUMMARY
✅ Migrated:
   Users: 0
   Tasks: 0
   Recurring Patterns: 0
```

**Run actual migration:**
```bash
python migrate_sqlite_to_postgres.py
```

Expected output:
```
🚀 SQLITE TO POSTGRESQL MIGRATION

📡 Connecting to databases...
✅ SQLite: sqlite:///./todo.db
✅ PostgreSQL: localhost:5432/todo_phase5

🔍 Analyzing SQLite database...
   📊 Data Summary:
      Users: 5
      Tasks: 23
      Recurring Patterns: 3

🏗️  Creating PostgreSQL tables...
   ✅ Tables created successfully

👤 Migrating users...
   ✅ Migrated 5 users

📝 Migrating tasks...
   ✅ Migrated 23 tasks

🔄 Migrating recurring patterns...
   ✅ Migrated 3 recurring patterns

✔️  Verifying migration...
   PostgreSQL counts:
      Users: 5
      Tasks: 23
      Recurring Patterns: 3

   ✅ Migration verified successfully!

📊 MIGRATION SUMMARY
✅ Migrated:
   Users: 5
   Tasks: 23
   Recurring Patterns: 3

⏱️  Duration: 1.23 seconds
```

### 4. Start Backend with PostgreSQL

```bash
uvicorn main:app --reload
```

Look for this output:
```
✅ Database configured for PRODUCTION environment (QueuePool: size=20, max_overflow=10)
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 5. Test the Connection

```bash
# Health check
curl http://localhost:8000/health

# List tasks (requires auth token)
curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Detailed Setup

### Local PostgreSQL Setup

#### Create Database Manually

If not using Docker:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create user
CREATE USER todouser WITH PASSWORD 'todopass123';

# Create database
CREATE DATABASE todo_phase5 OWNER todouser;

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE todo_phase5 TO todouser;

# Exit
\q
```

#### Verify Connection

```bash
# Using psql
psql -U todouser -d todo_phase5 -h localhost

# You should see:
# todo_phase5=>
```

### Environment Configuration

#### Development (SQLite)

```bash
# .env
ENVIRONMENT=development
# DATABASE_URL not set (uses SQLite automatically)
```

#### Production (PostgreSQL)

```bash
# .env
ENVIRONMENT=production
DATABASE_URL=postgresql://todouser:todopass123@localhost:5432/todo_phase5
```

#### Serverless (Vercel/Railway)

```bash
# .env
ENVIRONMENT=serverless
DATABASE_URL=postgresql://user:pass@neon-host.aws.neon.tech/dbname?sslmode=require
```

### Connection URL Formats

**Local PostgreSQL:**
```
postgresql://username:password@localhost:5432/database_name
```

**Docker Compose:**
```
postgresql://todouser:todopass123@postgres:5432/todo_phase5
```

**Kubernetes:**
```
postgresql://todouser:todopass123@postgres.default.svc.cluster.local:5432/todo_phase5
```

**Neon (Serverless):**
```
postgresql://user:pass@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Supabase:**
```
postgresql://postgres.[project-ref].supabase.co:5432/postgres?sslmode=require
```

---

## Migration Process

### Step-by-Step Migration

#### 1. Backup SQLite Database

```bash
# Create backup
cp todo.db todo.db.backup.$(date +%Y%m%d_%H%M%S)

# Or export to SQL
sqlite3 todo.db .dump > sqlite_backup.sql
```

#### 2. Prepare PostgreSQL

**Start PostgreSQL (if not running):**
```bash
docker start postgres-todo
# Or
brew services start postgresql@15
```

**Verify connectivity:**
```bash
psql -U todouser -d todo_phase5 -h localhost -c "SELECT 1;"
# Should output: 1
```

#### 3. Run Migration Script

**Test with dry-run:**
```bash
python migrate_sqlite_to_postgres.py --dry-run
```

**Execute migration:**
```bash
python migrate_sqlite_to_postgres.py
```

**Custom paths:**
```bash
# Custom SQLite path
python migrate_sqlite_to_postgres.py --sqlite-path /path/to/custom.db

# Custom PostgreSQL URL
python migrate_sqlite_to_postgres.py \
  --postgres-url "postgresql://user:pass@host:5432/dbname"
```

#### 4. Verify Data

**Check PostgreSQL:**
```bash
psql -U todouser -d todo_phase5 -h localhost
```

```sql
-- Count records
SELECT 'users' as table_name, COUNT(*) FROM users
UNION ALL
SELECT 'tasks', COUNT(*) FROM tasks
UNION ALL
SELECT 'recurring_patterns', COUNT(*) FROM recurring_patterns;

-- Sample users
SELECT id, email, username, created_at FROM users LIMIT 5;

-- Sample tasks
SELECT id, title, completed, user_id, created_at FROM tasks LIMIT 5;
```

#### 5. Switch Application to PostgreSQL

**Update `.env`:**
```bash
ENVIRONMENT=production
DATABASE_URL=postgresql://todouser:todopass123@localhost:5432/todo_phase5
```

**Restart backend:**
```bash
uvicorn main:app --reload
```

**Test endpoints:**
```bash
# Health check
curl http://localhost:8000/health

# Get tasks (after login)
curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Verification

### Automated Verification

The migration script includes built-in verification:
- Counts rows in source (SQLite) and destination (PostgreSQL)
- Compares counts to ensure completeness
- Reports any mismatches

### Manual Verification Checklist

- [ ] PostgreSQL server is running
- [ ] Database `todo_phase5` exists
- [ ] All tables created (users, tasks, recurring_patterns)
- [ ] Row counts match SQLite
- [ ] Backend starts without errors
- [ ] Authentication works (login/register)
- [ ] Tasks CRUD operations work
- [ ] Recurring tasks feature works
- [ ] Kafka consumer connects successfully
- [ ] WebSocket connections work

### SQL Verification Queries

```sql
-- Table sizes
SELECT
  table_name,
  pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) AS size
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY pg_total_relation_size(quote_ident(table_name)) DESC;

-- Data integrity checks
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'tasks', COUNT(*) FROM tasks
UNION ALL
SELECT 'recurring_patterns', COUNT(*) FROM recurring_patterns;

-- Foreign key validation
SELECT COUNT(*) as orphaned_tasks
FROM tasks t
LEFT JOIN users u ON t.user_id = u.id
WHERE u.id IS NULL;
-- Should return 0

-- Date range check
SELECT
  MIN(created_at) as oldest,
  MAX(created_at) as newest
FROM tasks;
```

---

## Rollback

### Switch Back to SQLite

If you need to revert to SQLite:

**1. Update `.env`:**
```bash
ENVIRONMENT=development
# DATABASE_URL=  # Comment out or remove
```

**2. Restart backend:**
```bash
uvicorn main:app --reload
```

You should see:
```
✅ Database configured for DEVELOPMENT environment (SQLite: sqlite:///./todo.db)
```

**3. Restore from backup (if needed):**
```bash
cp todo.db.backup.20260207_120000 todo.db
```

### Recreate PostgreSQL from Backup

**Using pg_dump:**
```bash
# Export from PostgreSQL
pg_dump -U todouser -h localhost todo_phase5 > postgres_backup.sql

# Restore later
psql -U todouser -h localhost -d todo_phase5 < postgres_backup.sql
```

**Using migration script (reverse):**
```bash
# Export SQLite from current PostgreSQL
# (Future enhancement - not yet implemented)
```

---

## Troubleshooting

### Connection Issues

#### Error: "psycopg2.OperationalError: could not connect to server"

**Cause:** PostgreSQL is not running or wrong credentials

**Solutions:**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres
# Or
pg_isready -h localhost -p 5432

# Start PostgreSQL
docker start postgres-todo

# Verify credentials
psql -U todouser -d todo_phase5 -h localhost
```

#### Error: "FATAL: database 'todo_phase5' does not exist"

**Solution:**
```bash
# Create database
psql -U postgres -h localhost -c "CREATE DATABASE todo_phase5 OWNER todouser;"
```

#### Error: "FATAL: role 'todouser' does not exist"

**Solution:**
```bash
# Create user
psql -U postgres -h localhost -c "CREATE USER todouser WITH PASSWORD 'todopass123';"
psql -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE todo_phase5 TO todouser;"
```

### Migration Issues

#### Error: "IntegrityError: duplicate key value violates unique constraint"

**Cause:** Target database already has data with conflicting IDs

**Solution:**
```bash
# Clear PostgreSQL tables
psql -U todouser -d todo_phase5 -h localhost -c "
  TRUNCATE users, tasks, recurring_patterns RESTART IDENTITY CASCADE;
"

# Re-run migration
python migrate_sqlite_to_postgres.py
```

#### Error: "Table already exists"

**Cause:** Tables exist from previous migration attempt

**Solution:**
```bash
# Drop and recreate tables
psql -U todouser -d todo_phase5 -h localhost -c "
  DROP TABLE IF EXISTS recurring_patterns, tasks, users CASCADE;
"

# Re-run migration
python migrate_sqlite_to_postgres.py
```

### Performance Issues

#### Slow queries after migration

**Check indexes:**
```sql
-- View indexes
SELECT tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public';

-- Create missing indexes if needed
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);
CREATE INDEX IF NOT EXISTS idx_recurring_user_id ON recurring_patterns(user_id);
```

#### Connection pool exhausted

**Symptoms:** "QueuePool limit of size 20 overflow 10 reached"

**Solutions:**
```python
# In database.py, increase pool size
pool_size=50,
max_overflow=20,
```

**Or reduce concurrent requests:**
```bash
# Limit uvicorn workers
uvicorn main:app --workers 2
```

### Backend Issues

#### Application still using SQLite after migration

**Check:**
```bash
# Verify DATABASE_URL is set
echo $DATABASE_URL  # Linux/Mac
echo %DATABASE_URL%  # Windows CMD
$env:DATABASE_URL   # Windows PowerShell

# Check .env file
cat .env | grep DATABASE_URL

# Verify backend logs show PostgreSQL
# Should see: "Database configured for PRODUCTION environment"
```

#### SQLAlchemy errors about missing columns

**Cause:** Schema mismatch between models and database

**Solution:**
```bash
# Use Alembic for schema migrations (if needed)
alembic upgrade head

# Or recreate tables
python migrate_sqlite_to_postgres.py --force-recreate
```

---

## Production Deployment

### Kubernetes

PostgreSQL is already configured in `kubernetes/postgres/`:

**Deploy PostgreSQL:**
```bash
kubectl apply -f kubernetes/postgres/
```

**Update backend environment:**
```yaml
# kubernetes/backend-simple.yaml
env:
  - name: DATABASE_URL
    value: "postgresql://todouser:todopass123@postgres:5432/todo_phase5"
  - name: ENVIRONMENT
    value: "production"
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: todouser
      POSTGRES_PASSWORD: todopass123
      POSTGRES_DB: todo_phase5
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: .
    environment:
      DATABASE_URL: postgresql://todouser:todopass123@postgres:5432/todo_phase5
      ENVIRONMENT: production
    depends_on:
      - postgres
    ports:
      - "8000:8000"

volumes:
  postgres_data:
```

**Run:**
```bash
docker-compose up -d
```

### Cloud Platforms

**Neon (Serverless PostgreSQL):**
1. Sign up at [neon.tech](https://neon.tech)
2. Create project and database
3. Copy connection string
4. Set in `.env`:
   ```
   ENVIRONMENT=serverless
   DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

**Supabase:**
1. Create project at [supabase.com](https://supabase.com)
2. Get connection string from Settings → Database
3. Use "Connection Pooling" URL for production

**Railway:**
1. Add PostgreSQL plugin
2. Copy DATABASE_URL from variables
3. Deploy backend with environment variables

---

## Best Practices

### Security

- ✅ Use strong passwords (generate with `openssl rand -base64 32`)
- ✅ Enable SSL/TLS for production (`?sslmode=require`)
- ✅ Restrict PostgreSQL access (firewall rules)
- ✅ Use secrets management (Kubernetes secrets, Vault)
- ✅ Rotate credentials regularly
- ❌ Never commit credentials to git
- ❌ Don't use default passwords in production

### Performance

- ✅ Use connection pooling (configured automatically)
- ✅ Monitor slow queries with `pg_stat_statements`
- ✅ Create indexes on frequently queried columns
- ✅ Use `pool_pre_ping` for connection health checks
- ✅ Set appropriate `pool_recycle` (1 hour default)

### Reliability

- ✅ Enable automated backups
- ✅ Test backup restoration regularly
- ✅ Monitor database metrics (CPU, memory, connections)
- ✅ Set up alerting for errors
- ✅ Use managed PostgreSQL in production (RDS, Cloud SQL)

---

## Next Steps

1. ✅ Complete SQLite to PostgreSQL migration
2. ✅ Verify all features work with PostgreSQL
3. 🔄 Configure Redis for WebSocket scaling (next task)
4. 🔄 Set up production Kafka cluster
5. 📊 Add Prometheus metrics
6. 🚀 Deploy to Kubernetes
7. 📈 Set up monitoring dashboards

---

## Support

**Documentation:**
- [PostgreSQL Official Docs](https://www.postgresql.org/docs/)
- [SQLAlchemy PostgreSQL Docs](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)
- [Kubernetes PostgreSQL Guide](./kubernetes/README.md)

**Common Commands:**
```bash
# Check PostgreSQL version
psql --version

# List databases
psql -U todouser -h localhost -l

# Connect to database
psql -U todouser -d todo_phase5 -h localhost

# Dump database
pg_dump -U todouser -h localhost todo_phase5 > backup.sql

# Restore database
psql -U todouser -h localhost -d todo_phase5 < backup.sql

# Check active connections
psql -U todouser -d todo_phase5 -h localhost -c "
  SELECT count(*) FROM pg_stat_activity
  WHERE datname = 'todo_phase5';
"
```

---

**Migration complete! Your Todo Phase5 application is now running on production-grade PostgreSQL. 🎉**
