from sqlmodel import Session, SQLModel, create_engine

DB_FILE = "tasks.db"

engine = create_engine(
    f"sqlite:///{DB_FILE}",
    echo=True,
    connect_args={"check_same_thread": False},
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session