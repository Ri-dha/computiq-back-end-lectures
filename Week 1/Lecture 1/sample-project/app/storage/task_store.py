"""DATA ACCESS LAYER (slide 2.9)

This layer's only job is storing and retrieving data. It knows nothing
about HTTP, status codes, or FastAPI.

Today the "database" is a plain Python dictionary that lives in memory,
so everything disappears when you stop the server. In Week 3 we replace
the body of these functions with real database calls using SQLModel —
and, because of this separation, nothing in routes/ or services/ has to
change. That is the whole point of layering.
"""

# Our fake database: {id: {"id": ..., "title": ..., "done": ...}}
_tasks: dict[int, dict] = {}

# Keeps track of the next id to hand out. A real database does this for us.
_next_id: int = 1


def get_all() -> list[dict]:
    """Return every task."""
    return list(_tasks.values())


def get_by_id(task_id: int) -> dict | None:
    """Return one task, or None if there's no task with that id."""
    return _tasks.get(task_id)


def create(title: str, done: bool) -> dict:
    """Store a new task and return it, with the id we assigned."""
    global _next_id

    task = {"id": _next_id, "title": title, "done": done}
    _tasks[_next_id] = task
    _next_id += 1
    return task


def update(task_id: int, title: str, done: bool) -> dict | None:
    """Replace an existing task. Returns None if it doesn't exist."""
    if task_id not in _tasks:
        return None

    task = {"id": task_id, "title": title, "done": done}
    _tasks[task_id] = task
    return task


def delete(task_id: int) -> bool:
    """Remove a task. Returns True if something was actually deleted."""
    if task_id not in _tasks:
        return False

    del _tasks[task_id]
    return True
