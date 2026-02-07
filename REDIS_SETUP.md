# Redis Setup Guide - WebSocket Scaling

Complete guide for setting up Redis to enable multi-instance WebSocket broadcasting.

## Table of Contents

1. [Overview](#overview)
2. [Why Redis for WebSocket?](#why-redis-for-websocket)
3. [Quick Start](#quick-start)
4. [Local Development](#local-development)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Cloud Providers](#cloud-providers)
7. [Configuration](#configuration)
8. [Testing](#testing)
9. [Monitoring](#monitoring)
10. [Troubleshooting](#troubleshooting)

---

## Overview

### Architecture

**Without Redis (Single Instance):**
```
User A ──► Backend Instance 1 ──► WebSocket (User A)
User B ──► Backend Instance 1 ──► WebSocket (User B)
```

**With Redis (Multi-Instance):**
```
User A ──► Backend Instance 1 ──┐
                                 ├──► Redis Pub/Sub ──► All Instances ──► All WebSockets
User B ──► Backend Instance 2 ──┘
```

### Features

- ✅ **Multi-Instance Broadcasting** - Events reach all connected users across all backend instances
- ✅ **Automatic Fallback** - Works without Redis (single-instance mode)
- ✅ **Minimal Changes** - Drop-in replacement for existing WebSocket manager
- ✅ **Production Ready** - Persistence, replication, and health checks

---

## Why Redis for WebSocket?

### Problem: Single-Instance Limitation

With a single backend instance:
- User on Instance 1 creates a task
- Only users connected to Instance 1 receive WebSocket updates
- Users on Instance 2 miss the update ❌

### Solution: Redis Pub/Sub

With Redis:
- User on Instance 1 creates a task
- Event published to Redis pub/sub channel
- All instances (1, 2, 3...) receive the event
- All connected users receive WebSocket updates ✅

### When Do You Need Redis?

**Single Instance (No Redis Needed):**
- Development environment
- Small deployments (<100 concurrent users)
- Single backend server

**Multi-Instance (Redis Required):**
- Production with load balancing
- Kubernetes with HPA (2+ replicas)
- High availability setup
- >100 concurrent WebSocket connections

---

## Quick Start

### 1. Start Redis

**Using Docker (Recommended for local testing):**
```bash
docker run -d \
  --name redis-todo \
  -p 6379:6379 \
  redis:7-alpine
```

**Verify:**
```bash
docker ps | grep redis-todo
# OR
redis-cli ping  # Should return PONG
```

### 2. Install Redis Python Client

```bash
pip install redis>=5.0.0
```

Already included in `requirements_kafka.txt` if you installed it.

### 3. Configure Environment

Update `.env`:
```bash
# Enable Redis for WebSocket scaling
REDIS_URL=redis://localhost:6379
```

### 4. Restart Backend

```bash
uvicorn main:app --reload
```

**Expected Output:**
```
✅ Redis WebSocket manager enabled: redis://localhost:6379
✅ Redis pub/sub initialized successfully
```

### 5. Test Multi-Instance

**Terminal 1:**
```bash
uvicorn main:app --port 8000
```

**Terminal 2:**
```bash
uvicorn main:app --port 8001
```

Create a task on port 8000, WebSocket clients on both ports receive the update! 🎉

---

## Local Development

### Option 1: Docker (Recommended)

```bash
# Start Redis
docker run -d \
  --name redis-todo \
  -p 6379:6379 \
  -v redis_data:/data \
  redis:7-alpine redis-server --appendonly yes

# Check logs
docker logs redis-todo

# Stop
docker stop redis-todo

# Remove
docker rm redis-todo
```

### Option 2: Native Installation

**macOS (Homebrew):**
```bash
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

**Windows:**
- Download from [Redis on Windows](https://github.com/microsoftarchive/redis/releases)
- Or use WSL2 with Linux installation

### Verify Installation

```bash
# Check if running
redis-cli ping
# Output: PONG

# Check version
redis-cli --version

# Monitor commands in real-time
redis-cli monitor
```

---

## Kubernetes Deployment

### Deploy Redis

**Apply Kubernetes manifests:**
```bash
kubectl apply -f kubernetes/redis/redis-deployment.yaml
```

**Verify deployment:**
```bash
# Check pods
kubectl get pods -n todo-phase5 | grep redis

# Check service
kubectl get svc -n todo-phase5 | grep redis

# Test connection
kubectl run -it --rm redis-test --image=redis:7-alpine --restart=Never -n todo-phase5 -- redis-cli -h redis ping
# Should output: PONG
```

### Update Backend Configuration

Redis URL is already configured in Helm values:
```yaml
env:
  - name: REDIS_URL
    value: "redis://redis:6379"
```

### Deploy Backend

```bash
helm upgrade --install todo-phase5-app helm/todo-phase5 -n todo-phase5
```

### Verify Multi-Instance Broadcasting

```bash
# Check backend pods (should be 2+)
kubectl get pods -n todo-phase5 | grep todo-backend

# Check logs from both pods
kubectl logs -f -n todo-phase5 -l app=todo-backend

# Look for:
# ✅ Redis WebSocket manager enabled
# ✅ Redis pub/sub initialized successfully
```

---

## Cloud Providers

### Redis Cloud (Recommended for Production)

**[Redis Cloud](https://redis.com/try-free/):**
- Free tier: 30MB
- Fully managed
- High availability
- Automatic backups

**Setup:**
1. Create account at redis.com
2. Create database
3. Copy endpoint (e.g., `redis-12345.c123.us-east-1-1.ec2.cloud.redislabs.com:12345`)
4. Get password
5. Set in `.env`:
   ```
   REDIS_URL=redis://:your-password@redis-12345.c123.us-east-1-1.ec2.cloud.redislabs.com:12345
   ```

### Upstash (Serverless Redis)

**[Upstash](https://upstash.com/):**
- Serverless pricing (pay per request)
- Free tier: 10K commands/day
- Global replication
- REST API included

**Setup:**
1. Create database at upstash.com
2. Copy Redis URL
3. Set in `.env`:
   ```
   REDIS_URL=redis://default:your-token@us1-alive-mantis-12345.upstash.io:6379
   ```

### AWS ElastiCache

**Setup:**
```bash
# Create ElastiCache cluster (using AWS CLI)
aws elasticache create-cache-cluster \
  --cache-cluster-id todo-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1

# Get endpoint
aws elasticache describe-cache-clusters \
  --cache-cluster-id todo-redis \
  --show-cache-node-info
```

**Connection:**
```
REDIS_URL=redis://todo-redis.abc123.0001.use1.cache.amazonaws.com:6379
```

### Google Cloud Memorystore

```bash
gcloud redis instances create todo-redis \
  --size=1 \
  --region=us-central1 \
  --tier=basic
```

### Azure Cache for Redis

```bash
az redis create \
  --resource-group todo-rg \
  --name todo-redis \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

---

## Configuration

### Environment Variables

```bash
# Redis URL (required for multi-instance)
REDIS_URL=redis://localhost:6379

# Redis with password
REDIS_URL=redis://:password@localhost:6379

# Redis with username and password
REDIS_URL=redis://username:password@localhost:6379

# Redis SSL/TLS
REDIS_URL=rediss://user:pass@host:6380  # Note: rediss:// (double 's')

# Redis Cloud example
REDIS_URL=redis://:your-password@redis-12345.cloud.redislabs.com:12345
```

### Redis Configuration File

For Kubernetes deployment, see `kubernetes/redis/redis-deployment.yaml`:

```yaml
# Key settings:
maxmemory: 256mb
maxmemory-policy: allkeys-lru  # Evict least recently used keys
appendonly: yes                 # Enable persistence
```

### Connection Pool Settings

Configured in `websocket_manager_redis.py`:
```python
max_connections=10  # Adjust based on backend replicas
```

---

## Testing

### Test Single Instance

```bash
# Start backend
uvicorn main:app --reload --port 8000

# In browser console:
const ws = new WebSocket('ws://localhost:8000/ws/tasks?token=YOUR_JWT');
ws.onmessage = (e) => console.log('Received:', JSON.parse(e.data));

# Create task via API (should trigger WebSocket message)
```

### Test Multi-Instance

**Terminal 1 (Instance 1):**
```bash
uvicorn main:app --port 8000
```

**Terminal 2 (Instance 2):**
```bash
uvicorn main:app --port 8001
```

**Terminal 3 (WebSocket Client on Instance 1):**
```javascript
const ws1 = new WebSocket('ws://localhost:8000/ws/tasks?token=JWT');
ws1.onmessage = (e) => console.log('[Port 8000]:', JSON.parse(e.data));
```

**Terminal 4 (WebSocket Client on Instance 2):**
```javascript
const ws2 = new WebSocket('ws://localhost:8001/ws/tasks?token=JWT');
ws2.onmessage = (e) => console.log('[Port 8001]:', JSON.parse(e.data));
```

**Create task on Instance 1:**
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer JWT" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Multi-Instance", "priority": "high"}'
```

**Expected:** Both WebSocket clients (port 8000 and 8001) receive the message! ✅

### Monitor Redis

```bash
# Real-time monitoring
redis-cli monitor

# Check pub/sub channels
redis-cli pubsub channels

# Check active subscriptions
redis-cli pubsub numsub websocket:broadcast:all

# Check memory usage
redis-cli info memory
```

---

## Monitoring

### Health Check Endpoint

Check WebSocket stats:
```bash
curl http://localhost:8000/ws/stats
```

Response:
```json
{
  "local_connections": 2,
  "local_users": 1,
  "redis_enabled": true,
  "total_instances": 3,
  "total_connections": 7
}
```

### Redis Metrics

```bash
# Connection count
redis-cli CLIENT LIST | wc -l

# Memory usage
redis-cli INFO memory | grep used_memory_human

# Pub/sub patterns
redis-cli PUBSUB CHANNELS

# Operations per second
redis-cli --stat
```

### Production Monitoring

**Prometheus + Grafana:**
1. Install Redis exporter
2. Scrape metrics
3. Create Grafana dashboard

**Key Metrics to Monitor:**
- Connection count
- Memory usage
- Pub/sub message rate
- Command latency
- Evicted keys

---

## Troubleshooting

### Issue: "redis package not installed"

**Error:**
```
⚠️  redis package not installed. Running in single-instance mode.
```

**Solution:**
```bash
pip install redis>=5.0.0
```

### Issue: "Failed to initialize Redis"

**Error:**
```
❌ Failed to initialize Redis: Error 111 connecting to localhost:6379
```

**Solutions:**
```bash
# Check if Redis is running
docker ps | grep redis
# OR
redis-cli ping

# Start Redis if not running
docker start redis-todo

# Check connection
telnet localhost 6379
```

### Issue: WebSocket messages not reaching all instances

**Symptoms:** Updates only visible on one instance

**Debug:**
```bash
# Check Redis pub/sub
redis-cli
> PUBSUB CHANNELS
# Should show: websocket:broadcast:all

# Check backend logs
# Look for: "📤 Published to Redis channel"

# Verify REDIS_URL is set
echo $REDIS_URL
```

### Issue: High Redis memory usage

**Check usage:**
```bash
redis-cli INFO memory
```

**Solution:**
```bash
# Set max memory (in redis.conf or command)
redis-cli CONFIG SET maxmemory 256mb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Issue: Connection timeouts

**Increase timeouts:**
```python
# In websocket_manager_redis.py
redis_client = await aioredis.from_url(
    redis_url,
    socket_connect_timeout=10,  # Increase
    socket_timeout=10
)
```

---

## Production Best Practices

### Security

- ✅ Enable authentication (`requirepass` in redis.conf)
- ✅ Use TLS/SSL for network encryption (`rediss://`)
- ✅ Restrict network access (firewall rules)
- ✅ Use Redis ACLs for fine-grained permissions
- ✅ Rotate passwords regularly
- ❌ Never expose Redis port publicly
- ❌ Don't use default password in production

### Performance

- ✅ Use connection pooling
- ✅ Set appropriate `maxmemory` limit
- ✅ Use `allkeys-lru` eviction policy
- ✅ Monitor slow queries (`CONFIG SET slowlog-log-slower-than 10000`)
- ✅ Enable persistence (AOF + RDB)

### High Availability

- ✅ Use Redis Sentinel for automatic failover
- ✅ Or use Redis Cluster for sharding
- ✅ Or use managed Redis (Redis Cloud, ElastiCache)
- ✅ Set up monitoring and alerting
- ✅ Regular backups

### Capacity Planning

**Estimate memory needs:**
```
Memory per connection = ~10KB
100 connections = 1MB
1,000 connections = 10MB
10,000 connections = 100MB
```

**Plus pub/sub overhead (~5-10MB)**

**Recommended sizes:**
- Small (<100 users): 64MB
- Medium (100-1,000 users): 256MB
- Large (1,000-10,000 users): 1GB
- Enterprise (>10,000 users): Redis Cluster

---

## Migration Guide

### From Single-Instance to Multi-Instance

**Step 1: Deploy Redis**
```bash
# Kubernetes
kubectl apply -f kubernetes/redis/

# Or Docker
docker run -d --name redis-todo -p 6379:6379 redis:7-alpine
```

**Step 2: Update Backend Configuration**
```bash
# Add to .env
REDIS_URL=redis://redis:6379
```

**Step 3: Restart Backend Instances**
```bash
# Kubernetes
kubectl rollout restart deployment/todo-backend -n todo-phase5

# Or local
uvicorn main:app --reload
```

**Step 4: Verify**
```bash
# Check logs
kubectl logs -n todo-phase5 -l app=todo-backend | grep Redis

# Should see:
# ✅ Redis WebSocket manager enabled
# ✅ Redis pub/sub initialized successfully
```

**Step 5: Test Multi-Instance Broadcasting**
- Connect WebSocket clients to different backend instances
- Create task on one instance
- Verify all clients receive update

---

## Next Steps

1. ✅ Set up Redis for multi-instance WebSocket scaling
2. ✅ Test with multiple backend instances
3. 🔄 Deploy to Kubernetes with HPA
4. 📊 Add Prometheus monitoring
5. 🚀 Configure production Redis cluster

---

**Redis setup complete! Your WebSocket system now scales horizontally across multiple backend instances. 🎉**
