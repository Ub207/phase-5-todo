# Deployment Guide - Phase5 Backend

## Railway Deployment Steps

### 1. Add Environment Variables

In Railway dashboard, add the following environment variables:

```
SECRET_KEY=KQ5IQP549W1OgTFY_eVy--Vh2czvbFOOisSglsw_ye8
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

**IMPORTANT**: The SECRET_KEY value above is a generated secure key. You can generate a new one with:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Verify Deployment

Once Railway redeploys, verify the following endpoints:

#### Health Check
```bash
curl https://todophase5-production.up.railway.app/health
```

Expected response:
```json
{"status": "ok", "environment": "production"}
```

#### Root Endpoint
```bash
curl https://todophase5-production.up.railway.app/
```

Should return API documentation with all available endpoints.

### 3. Test Authentication Flow

#### Register a User
```bash
curl -X POST https://todophase5-production.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "name": "Test User"
  }'
```

Expected response (201 Created):
```json
{
  "user": {
    "id": 1,
    "email": "test@example.com",
    "name": "Test User",
    "created_at": "2026-02-04T..."
  },
  "token": "eyJ..."
}
```

#### Login
```bash
curl -X POST https://todophase5-production.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

#### Create Task
```bash
TOKEN="your-jwt-token-here"
USER_ID=1

curl -X POST https://todophase5-production.up.railway.app/api/tasks/$USER_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "This is a test task",
    "due_date": "2026-02-10"
  }'
```

#### Get Tasks
```bash
curl https://todophase5-production.up.railway.app/api/tasks/$USER_ID \
  -H "Authorization: Bearer $TOKEN"
```

#### Complete Task
```bash
TASK_ID=1

curl -X PUT https://todophase5-production.up.railway.app/api/tasks/$USER_ID/$TASK_ID/complete \
  -H "Authorization: Bearer $TOKEN"
```

#### Delete Task
```bash
curl -X DELETE https://todophase5-production.up.railway.app/api/tasks/$USER_ID/$TASK_ID \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Verify Backward Compatibility

Test that the existing recurring endpoint still works:
```bash
curl https://todophase5-production.up.railway.app/recurring/run
```

## API Documentation

Once deployed, interactive API documentation is available at:
- Swagger UI: https://todophase5-production.up.railway.app/docs
- ReDoc: https://todophase5-production.up.railway.app/redoc

## Security Notes

1. **SECRET_KEY**: Must be kept secure and never committed to git
2. **Password Policy**: Minimum 8 characters (enforced by Pydantic)
3. **Token Expiry**: 30 days (configurable via ACCESS_TOKEN_EXPIRE_MINUTES)
4. **CORS**: Configured for production frontend domain and localhost

## Database

- SQLite database stored at `/tmp/todo.db` on Railway (Linux)
- Local development uses `./todo.db` (Windows-compatible)
- Database tables auto-created on startup
- User passwords hashed with bcrypt (cost factor 12)

## Troubleshooting

### Issue: 401 Unauthorized
- Verify token is included in Authorization header as: `Bearer <token>`
- Check if token has expired (30-day limit)
- Verify SECRET_KEY matches between token generation and validation

### Issue: 403 Forbidden
- User is trying to access another user's resources
- Verify userId in URL matches the authenticated user's ID

### Issue: 409 Conflict (Registration)
- Email already registered
- Use login endpoint instead or register with different email
