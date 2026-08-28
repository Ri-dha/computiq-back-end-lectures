"""BUSINESS LOGIC LAYER (slide 2.9)

The rules of the app live here: "can this be done? is this allowed?"

This layer talks to the storage layer, but it still knows nothing about
HTTP. Notice the import below — this is exactly the module/package
importing we covered in section 4.
"""

from app.storage import task_store


def list_tasks() -> list[dict]:
    return task_store.get_all()


def get_task(task_id: int) -> dict | None:
    return task_store.get_by_id(task_id)


def create_task(title: str, done: bool) -> dict:
    """A business rule: a task must actually have a title."""
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("Task title cannot be empty.")

    return task_store.create(clean_title, done)


def update_task(task_id: int, title: str, done: bool) -> dict | None:
    """Same rule applies on update — rules live in ONE place."""
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("Task title cannot be empty.")

    return task_store.update(task_id, clean_title, done)


def delete_task(task_id: int) -> bool:
    return task_store.delete(task_id)
