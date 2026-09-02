# CRUD API _w2a1
Fly rankAI Internship Assignment, backend engineering ex1

# Task Management API

A simple, in-memory CRUD API for managing tasks, built with Python and FastAPI. This project demonstrates basic API routing, data validation with Pydantic, HTTP status code handling, and auto-generated Swagger UI documentation.

## How to Install & Run

1. Make sure you have Python installed.
2. Save the API code in a file named `main.py`.
3. Run the following command in your terminal to install the requirements and start the development server:

```bash
pip install fastapi uvicorn pydantic && uvicorn main:app --reload
```
for uv
```bash
uv run --with fastapi --with uvicorn --with pydantic uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Root info (API name, version, available endpoints) |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/tasks` | Retrieve all tasks |
| `GET` | `/tasks/{item_id}` | Retrieve a specific task by ID |
| `POST` | `/tasks` | Create a new task (Requires JSON body with `title`) |
| `PUT` | `/tasks/{item_id}` | Update an existing task's `title` or `done` status |
| `DELETE` | `/tasks/{item_id}` | Delete a task |

## Example Request

Here is an example of creating a new task using `curl`:

```bash
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Study FastAPI"}'
```
Correct response:
```bash
HTTP/1.1 201 Created
date: Mon, 10 Aug 2026 16:33:41 GMT
server: uvicorn
content-length: 45
content-type: application/json

{"id":4,"title":"Study FastAPI","done":false}
```

## Interactive Documentation (Swagger UI)

FastAPI automatically generates interactive API documentation. Once the server is running, you can access it at `http://localhost:8000/docs`.

![Swagger UI Screenshot](image.png)
