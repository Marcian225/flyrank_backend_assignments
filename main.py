from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
class TaskCreate(BaseModel):
    title: str | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

app = FastAPI()


tasks = [
    {"id": 1, "title": "task1", "done": True},
    {"id": 2, "title": "task2", "done": False},
    {"id": 3, "title": "task3", "done": False},
    ]

@app.get("/")
async def root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health",summary = "Health check endpoint")
async def health_check():
    return { "status": "ok" }

@app.get("/tasks", summary="Retrieve all tasks")
async def get_all_tasks():
    return tasks

@app.get("/tasks/{item_id}", summary="Retrieve a specific task by ID")
async def get_task(item_id: int):
    for task in tasks:
        if task["id"] == item_id:
            return task

    return JSONResponse(
        status_code = 404,
        content = {"error": f"Task {item_id} not found"}
    )

@app.post("/tasks", status_code=201, summary="Create a new task")
async def add_task(item:TaskCreate):
    if item.title and item.title.strip():
        newid = max((task["id"] for task in tasks), default=0) +1
        newtask = {"id": newid, "title": item.title, "done": False}
        tasks.append(newtask)
        return newtask
    else:
        return JSONResponse(
            status_code = 400,
            content = {"error": "Bad Request"}
        )
    
@app.put("/tasks/{item_id}", status_code = 200, summary="Update an existing task")
async def update_task(item_id: int, item:TaskUpdate):
    if item == None or (item.title == None and item.done == None) or (item.title != None and item.title.strip() == ""):
        return JSONResponse(
                status_code = 400,
                content = {"error": "Empty/Invalid body"}
            )
    
    for task in tasks:
        if task["id"] == item_id:
            if item.title and item.title.strip():
                task["title"] = item.title

            if item.done != None:
                task["done"] = item.done

            return task

    return JSONResponse(
        status_code = 404,
        content = {"error": "Unknown id"}
    )

@app.delete("/tasks/{item_id}", status_code = 204, summary="Delete a task")
async def delete_task(item_id: int):
    for task in tasks:
        if task["id"] == item_id:
            tasks.remove(task)
            return

    return JSONResponse(
        status_code = 404,
        content = {"error": "Unknown id"}
    )