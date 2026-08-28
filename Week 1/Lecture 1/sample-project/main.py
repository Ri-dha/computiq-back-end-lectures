"""Entry point — this is the file uvicorn runs.

Notice how small it is. It creates the app and plugs in the routes.
All the real work lives inside the app/ package.

Run it with:
    uvicorn main:app --reload
"""

from fastapi import FastAPI

from app.routes import tasks

app = FastAPI(
    title="Task Manager",
    description="Week 1 · Lecture 1 demo — a simple CRUD backend.",
)

# Plug the /tasks endpoints into the app.
app.include_router(tasks.router)


@app.get("/")
def read_root():
    """The same 'hello world' endpoint from the slides — proof the server is up."""
    return {"message": "Hello, backend world!"}
