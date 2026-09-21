# Task Management API

A CRUD API for managing tasks, built with Python, FastAPI and SQLModel, running against PostgreSQL. The app and its database both run in Docker containers, so the whole stack starts with one command and needs no local Python or PostgreSQL installation.

Built for the FlyRank AI backend engineering internship. Storage has moved through three stages: an in-memory list (A1), a SQLite file (A2), and now a PostgreSQL server in a container (A3). The API surface stayed the same throughout.

## Running it

Requires only Docker Desktop or Podman — confirm with `docker --version`.

```bash
git clone <repo-url>
cd flyrank_backend_assignments
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

The app reads `DATABASE_URL` from the environment and refuses to start if it's missing.

**Running via `docker compose up` needs no configuration** — compose injects `DATABASE_URL` (see the `api` service in `compose.yaml`). No `.env` file is used.

`.env` is only needed for the optional non-Docker workflow below. In that case, `cp .env.example .env` and edit it. `.env` is git-ignored because it holds a password; `.env.example` is committed and documents the required keys.

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

## Interactive documentation (Swagger UI)

FastAPI generates the docs automatically, served at `http://localhost:8000/docs` while the stack is running.

![Swagger UI Screenshot](/images/image.png)

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

Compose puts both on a private network where each service is reachable by name, which is why `DATABASE_URL` uses the host `db` rather than `localhost`. The database publishes no port to the host, since only the API talks to it.

PostgreSQL is pinned to 17 deliberately: version 18 changed the expected data mount path to `/var/lib/postgresql`, and the mount used here fails against it.

`.dockerignore` keeps `.venv`, `.git` and `.env` out of the build context, so no secrets are baked into the image — configuration is injected at run time instead.

## Running outside Docker (optional)

Useful during development, since `fastapi dev` reloads on file changes. The database must be reachable at `localhost:5432`, so add a published port to the `db` service in `compose.yaml`:

```yaml
    ports:
      - "5432:5432"
```

Then:

```bash
docker compose up db          # database only
cp .env.example .env          # match the password in compose.yaml
uv sync
uv run fastapi dev main.py
```

## Troubleshooting

**`password authentication failed for user "postgres"`** — something other than the container may hold port 5432. Check with `ss -ltnp | grep 5432`; a natively installed PostgreSQL answers first and rejects the container's password. Stop it with `sudo service postgresql stop`.

**`Connection refused`** — nothing is listening. Confirm the stack is up with `docker compose ps`, then restart it. On WSL, Docker's port forwarding doesn't always claim a port that was occupied when the container started.

**Code changes not taking effect** — compose reuses the image it built earlier. Use `docker compose up --build` after editing application code.


## A4 Stage 5 Requirement (Swagger UI Documentation with bearer auth)
![alt text](/images/image-6.png)
![alt text](/images/image-7.png)
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