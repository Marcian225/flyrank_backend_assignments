from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session, select
from database import engine, Task

class TaskCreate(BaseModel):
    title: str | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

app = FastAPI()


# tasks = [
#     {"id": 1, "title": "task1", "done": True},
#     {"id": 2, "title": "task2", "done": False},
#     {"id": 3, "title": "task3", "done": False},
#     ]

@app.get("/")
async def root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health",summary = "Health check endpoint")
async def health_check():
    return { "status": "ok" }

@app.get("/tasks", summary="Retrieve all tasks")
async def get_all_tasks():
    with Session(engine) as session:
        return session.exec(select(Task)).all()


@app.get("/tasks/{item_id}", summary="Retrieve a specific task by ID")
async def get_task(item_id: int):
    # for task in tasks:
    #     if task["id"] == item_id:
    #         return task

    with Session(engine) as session:
        task = session.get(Task, item_id)
        if task: return task

    return JSONResponse(
        status_code = 404,
        content = {"error": f"Task {item_id} not found"}
    )

@app.post("/tasks", status_code=201, summary="Create a new task")
async def add_task(item:TaskCreate):

    if item.title and item.title.strip():
        with Session(engine) as session:
            new_task = Task(title = item.title, done = False)
            session.add(new_task)
            session.commit()
            session.refresh(new_task)
            return new_task
        # newid = max((task["id"] for task in tasks), default=0) +1
        # newtask = {"id": newid, "title": item.title, "done": False}
        # tasks.append(newtask)
        # return newtask
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

    with Session(engine) as session:
        # targetalt = session.get(Task,item_id)
        target = session.exec(select(Task).where(Task.id == item_id)).first()

        if not target:
            return JSONResponse(
                status_code = 404,
                content = {"error": "Unknown id"}
            )

        if item.title and item.title.strip():
            target.title = item.title
        if item.done != None:
            target.done = item.done
        session.add(target)
        session.commit()
        session.refresh(target)
        return target
    
    # for task in tasks:
    #     if task["id"] == item_id:
    #         if item.title and item.title.strip():
    #             task["title"] = item.title
    #         if item.done != None:
    #             task["done"] = item.done
    #         return task


@app.delete("/tasks/{item_id}", status_code = 204, summary="Delete a task")
async def delete_task(item_id: int):
    # for task in tasks:
    #     if task["id"] == item_id:
    #         tasks.remove(task)
    #         return

    with Session(engine) as session:
        target = session.get(Task,item_id)

        if target:
            session.delete(target)
            session.commit()
            return
        else:
            return JSONResponse(
                status_code = 404,
                content = {"error": "Unknown id"}
            )