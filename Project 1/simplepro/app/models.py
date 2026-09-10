from sqlmodel import Field, SQLModel


class TaskBase(SQLModel):
    """The fields that everything shares."""
    title: str = Field(min_length=1, max_length=100)
    done: bool = False
    priority: int = Field(default=3, ge=1, le=5)


class Task(TaskBase, table=True):
    """The database table. Only this one has table=True."""
    id: int | None = Field(default=None, primary_key=True)
    internal_note: str = ""


class TaskCreate(TaskBase):
    """What a client may send to POST and PUT."""
    pass


class TaskUpdate(SQLModel):
    """What a client may send to PATCH — every field optional."""
    title: str | None = Field(default=None, min_length=1, max_length=100)
    done: bool | None = Field(default=None)
    priority: int | None = Field(default=None, ge=1, le=5)


class TaskPublic(TaskBase):
    """What the client is allowed to see."""
    id: int