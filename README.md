# Task Management API

A CRUD API for managing tasks, built with Python, FastAPI and SQLModel, running against PostgreSQL, with user authentication through Supabase Auth. The app and its database both run in Docker containers, so the whole stack starts with one command and needs no local Python or PostgreSQL installation.

Built for the FlyRank AI backend engineering internship. Storage has moved through three stages: an in-memory list (A1), a SQLite file (A2), and now a PostgreSQL server in a container (A3). A4 added authentication: sign up, log in, log out, and routes that answer only to logged-in users. Supabase stores the accounts, hashes the passwords and signs the tokens; this API only receives tokens and verifies them.

## Running it

Requires Docker Desktop or Podman (confirm with `docker --version`) and a free [Supabase](https://supabase.com) project — see [Supabase setup](#supabase-setup) below.

```bash
git clone <repo-url>
cd flyrank_backend_assignments
cp .env.example .env        # then fill in your Supabase values
docker compose up
```

The API is then at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

On first start the app creates the `tasks` table and seeds three example tasks. Seeding only happens when the table is empty, so restarts don't duplicate data.

To stop:

```bash
docker compose down        # keeps your data
docker compose down -v     # also deletes the volume — destroys your data
```

## Configuration

The app reads three variables from the environment and refuses to start if any is missing:

| Variable | Purpose |
| :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string |
| `SUPABASE_URL` | Your Supabase project URL, e.g. `https://abcdefghijklmnopqrst.supabase.co` |
| `SUPABASE_KEY` | Your Supabase **anon** (or **publishable**) key |

**Running via `docker compose up`**, compose injects `DATABASE_URL` directly (see the `api` service in `compose.yaml`) and reads the two Supabase values from `.env` via `env_file`. The `DATABASE_URL` line in `.env` is ignored in this case — compose's own `environment:` entry takes precedence, so the container always uses the `db` host.

**Running outside Docker**, all three come from `.env`.

`.env` is git-ignored because it holds secrets; `.env.example` is committed and documents the required keys.

### Supabase setup

1. Create a free project at [supabase.com](https://supabase.com).
2. In **Authentication → Sign In / Providers → Email**, turn **Confirm email** off. Otherwise new users must confirm by email before they can log in, and `/auth/login` will reject them.
3. Copy your **Project URL** into `SUPABASE_URL`. Use the bare URL — if the dashboard shows it with `/rest/v1/` on the end, strip that off.
4. Copy your **anon** or **publishable** key (Project Settings → API Keys) into `SUPABASE_KEY`. Never use the `service_role` or secret key here — it bypasses all security.

## API endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Root info (API name, version, available endpoints) |
| `GET` | `/health` | Health check |
| `GET` | `/tasks` | Retrieve all tasks |
| `GET` | `/tasks/{item_id}` | Retrieve a task by ID |
| `POST` | `/tasks` | Create a task (JSON body with `title`) |
| `PUT` | `/tasks/{item_id}` | Update a task's `title` or `done` |
| `DELETE` | `/tasks/{item_id}` | Delete a task |

Status codes: `201` create, `200` read and update, `204` delete, `400` invalid body, `404` unknown id.

### Authentication endpoints

| Method | Endpoint | Description | Auth header |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/signup` | Create an account (JSON body with `email` and `password`) | none |
| `POST` | `/auth/login` | Log in; returns `access_token` and `refresh_token` | none |
| `POST` | `/auth/logout` | End the current session | `Authorization: Bearer <token>` |
| `GET` | `/protected/profile` | The logged-in user's `id`, `email` and `created_at` | `Authorization: Bearer <token>` |
| `GET` | `/protected/dashboard` | Example second protected route | `Authorization: Bearer <token>` |
| `GET` | `/public/info` | Public message, open to anyone | none |

Status codes: `201` signup, `200` login and reads, `204` logout, `400` missing email or password, `401` wrong credentials or a missing, malformed, invalid, expired or logged-out token.

All protected routes share one FastAPI dependency, `get_current_user`, which extracts the bearer token and asks Supabase to verify it before the route body runs. Protecting a new route takes one parameter: `user = Depends(get_current_user)`.

## Example request

```bash
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Study FastAPI"}'
```

```
HTTP/1.1 201 Created
date: Mon, 10 Aug 2026 16:33:41 GMT
server: uvicorn
content-length: 45
content-type: application/json

{"id":4,"title":"Study FastAPI","done":false}
```

## Example auth flow

```bash
# Sign up
curl -i -X POST http://localhost:8000/auth/signup -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"password123"}'

# Log in and save the access token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"password123"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Call a protected route -> 200
curl -i http://localhost:8000/protected/profile -H "Authorization: Bearer $TOKEN"

# Log out -> 204; the same token is now rejected with 401
curl -i -X POST http://localhost:8000/auth/logout -H "Authorization: Bearer $TOKEN"
```

Access tokens expire after an hour; log in again to get a new one.

## Interactive documentation (Swagger UI)

FastAPI generates the docs automatically, served at `http://localhost:8000/docs` while the stack is running.

Protected routes show a padlock. To call them from the browser: run `POST /auth/login` with **Try it out**, copy the `access_token`, click **Authorize** at the top right and paste the token alone — Swagger adds the `Bearer ` prefix itself.

![Swagger UI with bearer auth](/images/image-6.png)
![Authorized call to the profile endpoint](/images/image-7.png)

## The data in PostgreSQL

Open a SQL prompt inside the database container (`\dt` lists tables, `\d tasks` describes the table, `\q` quits):

```bash
docker compose exec db psql -U postgres -d tasks
```

Or list the table and rows directly:

```bash
docker compose exec db psql -U postgres -d tasks -c "\dt" -c "SELECT * FROM tasks;"
```

![Tasks table in PostgreSQL](/images/image-5.png)

`done` is stored as a real PostgreSQL `BOOLEAN` (`t`/`f`). The same SQLModel class produced an integer column under SQLite — the ORM picks column types from the database dialect.

## How it fits together

`compose.yaml` defines two services:

- **`api`** — built from the `Dockerfile` here (`python:3.12-slim` plus `uv`, dependencies installed from `uv.lock`). Port 8000 is published to your machine.
- **`db`** — the official `postgres:17` image, storing data in a named volume so it survives containers being removed and recreated.

Compose puts both on a private network where each service is reachable by name, which is why `DATABASE_URL` uses the host `db` rather than `localhost`. The database also publishes port 5432 to the host, so the app can run outside Docker during development (see below).

PostgreSQL is pinned to 17 deliberately: version 18 changed the expected data mount path to `/var/lib/postgresql`, and the mount used here fails against it.

`.dockerignore` keeps `.venv`, `.git` and `.env` out of the build context, so no secrets are baked into the image — configuration is injected at run time instead.

## Running outside Docker (optional)

Useful during development, since `fastapi dev` reloads on file changes. The app then runs on your machine and reaches the database at `localhost:5432`, which compose already publishes.

```bash
docker compose up -d db       # database only
cp .env.example .env          # match the password in compose.yaml, add Supabase values
uv sync
uv run fastapi dev main.py
```

If the `api` container is also running, it holds port 8000 and `fastapi dev` will fail to start. Stop it first with `docker compose stop api`.

## Troubleshooting

**`password authentication failed for user "postgres"`** — something other than the container may hold port 5432. Check with `ss -ltnp | grep 5432`; a natively installed PostgreSQL answers first and rejects the container's password. Stop it with `sudo service postgresql stop`.

**`Connection refused`** — nothing is listening. Confirm the stack is up with `docker compose ps`, then restart it. On WSL, Docker's port forwarding doesn't always claim a port that was occupied when the container started.

**Code changes not taking effect** — compose reuses the image it built earlier. Use `docker compose up --build` after editing application code.

**`env file .../.env not found`** — compose needs a `.env` for the Supabase values. Run `cp .env.example .env` and fill it in.

**`SUPABASE_URL / SUPABASE_KEY are not set`** — `.env` exists but the Supabase lines are missing or empty.

**Signup works but login returns `401`** — email confirmation is still on in your Supabase project. See [Supabase setup](#supabase-setup).

**A token that worked now returns `401`** — it expired (tokens last an hour) or you logged out with it. Log in again.

## Previous assignments

Requirements below were met in earlier assignments against the storage backend used at the time. The current stack is PostgreSQL, described above.

### A2 — SQLite via DB Browser

A2 stored tasks in a SQLite file (`tasks.db`) through SQLModel, chosen at that stage because it needs no separate server and keeps everything in one file that survives restarts.

![DB Browser for SQLite](/images/image-1.png)

Running this in DB Browser's "Execute SQL" tab:

```sql
UPDATE tasks SET done = 1;
```

![Executing SQL](/images/image-4.png)

Result after calling `GET /tasks` on the running API:

![All tasks marked done](/images/image-3.png)

All tasks came back with `done: true` without a server restart, confirming the API read live from the database file rather than from memory.