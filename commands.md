# Task API — curl cheat sheet

All commands target `http://localhost:8000` and are single-line, so they paste cleanly.

## Info

```bash
# Root info -> 200
curl -i http://localhost:8000/

# Health check -> 200
curl -i http://localhost:8000/health

# Public info -> 200
curl -i http://localhost:8000/public/info
```

## Tasks

```bash
# List all -> 200
curl -i http://localhost:8000/tasks

# Get one -> 200
curl -i http://localhost:8000/tasks/1

# Get missing -> 404
curl -i http://localhost:8000/tasks/9999

# Create -> 201
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"New task"}'

# Create with empty title -> 400
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"   "}'

# Create with no title -> 400
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{}'

# Update title -> 200
curl -i -X PUT http://localhost:8000/tasks/1 -H "Content-Type: application/json" -d '{"title":"Renamed task"}'

# Update done -> 200
curl -i -X PUT http://localhost:8000/tasks/1 -H "Content-Type: application/json" -d '{"done":true}'

# Update both -> 200
curl -i -X PUT http://localhost:8000/tasks/1 -H "Content-Type: application/json" -d '{"title":"Renamed again","done":false}'

# Update with empty body -> 400
curl -i -X PUT http://localhost:8000/tasks/1 -H "Content-Type: application/json" -d '{}'

# Update missing -> 404
curl -i -X PUT http://localhost:8000/tasks/9999 -H "Content-Type: application/json" -d '{"done":true}'

# Delete -> 204 (pick an id that exists; check with GET /tasks first)
curl -i -X DELETE http://localhost:8000/tasks/3

# Delete missing -> 404
curl -i -X DELETE http://localhost:8000/tasks/9999
```

## Auth

```bash
# Sign up -> 201 (a second run with the same email will fail: already registered)
curl -i -X POST http://localhost:8000/auth/signup -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"password123"}'

# Sign up with no password -> 400
curl -i -X POST http://localhost:8000/auth/signup -H "Content-Type: application/json" -d '{"email":"test@example.com"}'

# Log in -> 200 with access_token and refresh_token
curl -i -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"password123"}'

# Log in with wrong password -> 401
curl -i -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"wrongpassword"}'

# Log in with missing field -> 400
curl -i -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"test@example.com"}'

# Log out 
curl -i -X POST http://localhost:8000/auth/logout -H "Authorization: Bearer $TOKEN"
```

## Save the token into a variable

Logs in and stores the access token in `$TOKEN`, so you don't have to copy it by hand. Lasts for the current terminal session; the token itself expires after an hour.

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"password123"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Check it worked
echo $TOKEN
```

## Protected profile

```bash
# Valid token -> 200 with id, email, created_at
curl -i http://localhost:8000/protected/profile -H "Authorization: Bearer $TOKEN"

# Tampered token (one character appended) -> 401 "Invalid or expired token"
curl -i http://localhost:8000/protected/profile -H "Authorization: Bearer ${TOKEN}x"

# Fake token -> 401 "Invalid or expired token"
curl -i http://localhost:8000/protected/profile -H "Authorization: Bearer abc123"

# No header -> 401 "Access token required"
curl -i http://localhost:8000/protected/profile

# Wrong scheme -> 401 "Access token required"
curl -i http://localhost:8000/protected/profile -H "Authorization: Basic abc123"

# Scheme with no token -> 401 "Access token required"
curl -i http://localhost:8000/protected/profile -H "Authorization: Bearer"

# Token with no scheme -> 401 "Access token required"
curl -i http://localhost:8000/protected/profile -H "Authorization: abc123"

curl -i http://localhost:8000/protected/dashboard -H "Authorization: Bearer $TOKEN"
curl -i http://localhost:8000/protected/dashboard -H "Authorization: Bearer ${TOKEN}x"

```