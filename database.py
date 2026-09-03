from sqlmodel import create_engine, SQLModel, Field, Session, select

DATABASE_URL = "sqlite:///tasks.db"

engine = create_engine(DATABASE_URL, echo=True)

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    id: int | None = Field(default=None, primary_key=True)
    title: str
    done: bool = False

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def seed_tasks():
    with Session(engine) as session:
        existing = session.exec(select(Task)).first()
        if existing == None:
            session.add_all([
                Task(title = "Buy milk"),
                Task(title = "Write report", done = True),
                Task(title = "Walk the dog")
            ])
            session.commit()
            print("seeded 3 tasks")
        else:
            print("Tasks already exist, skeeping seed")

if __name__ == "__main__":
    create_db_and_tables()
    seed_tasks()