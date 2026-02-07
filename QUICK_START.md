# ⚡ Quick Start - Copy & Paste Commands

## 1. Install Dependencies
```bash
pip install -r requirements_kafka.txt
```

## 2. Start Kafka (if not running)
```bash
# Using Docker (recommended)
docker run -d --name kafka -p 9092:9092 apache/kafka:latest

# Verify Kafka is running
netstat -an | findstr "9092"
```

## 3. Start FastAPI Backend
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
✅ Database initialized successfully
✅ Kafka consumer service started in background
✅ Kafka consumer created successfully: localhost:9092
🚀 Kafka consumer service started. Listening for events...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 4. Test Integration
```bash
# Terminal 2 (while backend is running)
python test_kafka_integration.py
```

**Expected Output:**
```
✅ ALL TESTS PASSED!
🎉 Your Kafka + FastAPI integration is working perfectly!
```

## 5. Send Test Events
```bash
python send_test_event.py
```

## 6. Check Status
```bash
# Health check
curl http://localhost:8000/health

# WebSocket stats
curl http://localhost:8000/ws/stats

# View recent tasks
curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 7. Monitor Database
```bash
# Count tasks
python -c "import sqlite3; conn = sqlite3.connect('todo.db'); print(f'Total tasks: {conn.execute(\"SELECT COUNT(*) FROM tasks\").fetchone()[0]}'); conn.close()"

# View recent tasks
python -c "import sqlite3; conn = sqlite3.connect('todo.db'); tasks = conn.execute('SELECT id, title, completed FROM tasks ORDER BY id DESC LIMIT 5').fetchall(); print('\n'.join([f'{t[0]}: {t[1]} (Completed: {bool(t[2])})' for t in tasks])); conn.close()"
```

## 8. Frontend WebSocket Connection
```javascript
const token = localStorage.getItem('token');
const ws = new WebSocket(`ws://localhost:8000/ws/tasks?token=${token}`);

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  console.log('Received:', msg.type, msg.data);
};

// Keepalive
setInterval(() => ws.send('ping'), 30000);
```

## Troubleshooting

### Kafka Not Running
```bash
# Check if Kafka is running
netstat -an | findstr "9092"

# Start Kafka with Docker
docker run -d --name kafka -p 9092:9092 apache/kafka:latest
```

### Backend Not Starting
```bash
# Check Python version (requires 3.8+)
python --version

# Reinstall dependencies
pip install -r requirements_kafka.txt

# Check for errors
python -c "from main import app"
```

### WebSocket Not Connecting
```bash
# Check CORS settings in main.py
# Add your frontend URL to allowed origins

# Test without authentication first
# Set token=None in WebSocket URL for testing
```

## Next Steps

1. ✅ Backend running with Kafka consumer
2. ✅ Integration tests passing
3. ✅ WebSocket endpoint available
4. 🚀 Integrate frontend (see `frontend_websocket_example.js`)
5. 🎉 Build real-time features!

## Documentation
- **Full Guide**: `KAFKA_INTEGRATION_GUIDE.md`
- **Summary**: `INTEGRATION_SUMMARY.md`
- **Frontend Example**: `frontend_websocket_example.js`
