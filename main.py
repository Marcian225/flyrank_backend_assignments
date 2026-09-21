from fastapi import FastAPI, Header, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session, select
from database import engine, Task
from contextlib import asynccontextmanager
from database import create_db_and_tables, seed_tasks
from supabase_client import supabase
from supabase_auth.errors import AuthApiError



class AuthCredentials(BaseModel):
    email: str | None = None
    password: str | None = None
class TaskCreate(BaseModel):
    title: str | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed_tasks()
    print("Server running and connected to Supabase")
    yield


app = FastAPI(lifespan=lifespan)


async def get_token(authorization: str | None = Header(default=None)) -> str:
    if authorization is None:
        raise HTTPException(status_code=401, detail="Access token required")
    scheme, _, token = authorization.partition(" ")
    token = token.strip()
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Access token required")
    return token

async def get_current_user(token: str = Depends(get_token)):
    try:
        return supabase.auth.get_user(token).user
    except AuthApiError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@app.get("/public/info", status_code=200, summary = "Gets public info")
async def get_info():
    return { "message": "Welcome stranger! This info is public." } 

@app.get("/protected/profile", status_code=200, summary = "Gets profile info")
async def get_profile(user = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "created_at": user.created_at}

@app.get("/protected/dashboard", status_code=200, summary = "Gets dashboard")
async def get_dashboard(user = Depends(get_current_user)):
    return {"info": "nice dashboard", "user email": user.email}

@app.post("/auth/logout", status_code=204, summary="Logs out the user")
async def logout(token = Depends(get_token)):
    supabase.auth.admin.sign_out(token)


@app.post("/auth/signup",status_code=201 ,summary="Signs up the new user")
async def signup(auth_data: AuthCredentials):
    if (auth_data.email and auth_data.email.strip()) and (auth_data.password and auth_data.password.strip()):
        response = supabase.auth.sign_up({
            "email": auth_data.email,
            "password": auth_data.password,
        })
        return response.user
    else:
        return JSONResponse(
            status_code = 400,
            content = {"error": "Email and password required"}
        )

@app.post("/auth/login",status_code=200 ,summary="Logs in the user")
async def login(auth_data: AuthCredentials):
    if (auth_data.email and auth_data.email.strip()) and (auth_data.password and auth_data.password.strip()):
        try:
            response = supabase.auth.sign_in_with_password({
                "email": auth_data.email,
                "password": auth_data.password
            })
        except AuthApiError:
            return JSONResponse(
                status_code= 401,
                content= {"error": "Invalid login credentials"}
            )
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }
    else:
        return JSONResponse(
            status_code = 400,
            content = {"error": "Email and password required"}
        )



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
                content = {"error": f"Task {item_id} not found"}
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
                content = {"error": f"Task {item_id} not found"}
            )