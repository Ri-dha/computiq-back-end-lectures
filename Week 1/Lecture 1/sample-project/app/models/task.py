"""Task shapes — what a task looks like going in and coming out.

This is the vocabulary of the app. Everything else imports from here.

Week 2 note: these are Pydantic models. Today just read them as
"a description of the fields a task has". We unpack Pydantic properly
in Lecture 2 / Week 2.
"""

from pydantic import BaseModel


class TaskCreate(BaseModel):
    """What the client SENDS when creating a task (no id — the server assigns it)."""

    title: str
    done: bool = False


class Task(BaseModel):
    """What the server SENDS BACK — same fields, plus the id it assigned."""

    id: int
    title: str
    done: bool
