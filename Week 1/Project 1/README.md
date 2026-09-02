# Project 1 — Build a Task API with FastAPI and SQLite

A step-by-step walkthrough. You start with an empty folder and finish with a working backend that stores tasks in a real database and survives being restarted.

Everything here builds on Week 1 · Lecture 1. The environment setup in Parts 1–5 is the checklist from that lecture, applied for real. Parts 6–9 go further than we covered in class — that is intentional, and every piece of it is flagged with the week where you'll learn how it actually works.

**How to use this.** Type the commands, don't copy-paste them where you can help it. Each part ends with a **Checkpoint** — an observable result. If your checkpoint doesn't match, stop and fix it there rather than continuing. Nearly every problem in this guide comes from a step that quietly failed three parts earlier. There's a Troubleshooting section at the end for the usual suspects.

---

## Part 0 — Before you start

You need **Python 3.10 or newer**. Check:

```bash
python --version
```

If that says "command not found" or shows a version starting with `2.`, try:

```bash
python3 --version
```

Whichever one gives you 3.10+ is *your* command. Use it everywhere this guide says `python`, and use the matching `pip3` wherever it says `pip`.

Don't have Python? Get it from [python.org/downloads](https://python.org/downloads) (or the Microsoft Store on Windows), then reopen your terminal and check again.

**Checkpoint:** `python --version` (or `python3 --version`) prints 3.10 or higher.

---

## Part 1 — Create the project folder

Four terminal commands do almost everything you need for now:

```bash
pwd             # where am I?
ls              # what's here?   (Windows: dir)
cd folder_name  # go into a folder
cd ..           # go up one level
```

Navigate to wherever you keep your coding projects — Desktop is fine — then create the folder and move into it:

```bash
mkdir project-1 && cd project-1
```

**Checkpoint:** `pwd` ends in `project-1`, and `ls` shows nothing. An empty folder is exactly right.

---

## Part 2 — Create the virtual environment

Here's the problem a virtual environment solves. Project A needs version 1.0 of some package; Project B needs version 2.0. Install packages globally and only one version can exist on your machine at a time — installing for one project silently breaks the other.

A virtual environment is an isolated folder holding its own copy of Python and its own installed packages. Every project gets one. This is standard professional practice, not a beginner training wheel.

Create it (the tool is built into Python — nothing to install):

```bash
python -m venv venv
```

That made a folder called `venv`. Now activate it.

**macOS / Linux:**

```bash
source venv/bin/activate
```

**Windows (PowerShell):**

```bash
venv\Scripts\Activate.ps1
```

Your prompt now starts with `(venv)`. That is your proof it worked, and you should glance at it every time something in this guide misbehaves.

```
(venv) yourname@laptop project-1 %
```

When you're finished working, `deactivate` turns it off. You'll need to activate again in every new terminal window — there is no way to make it stick, and forgetting is the single most common source of confusing errors.

**Checkpoint:** your prompt shows `(venv)`.

---

## Part 3 — Install the packages

With the venv **active**, install the three packages this project needs:

```bash
pip install fastapi uvicorn sqlmodel
```

- **fastapi** — the framework. It's what lets you define what your app does. Week 2 is entirely about this.
- **uvicorn** — the server that actually runs your app and speaks HTTP to the outside world. FastAPI needs both.
- **sqlmodel** — talks to a database from Python code. This is Week 3's tool; you're getting an early look.

See what landed:

```bash
pip list
```

You'll see more than three packages. The extras are dependencies — packages your packages needed. That's normal and you don't have to care about them.

**Checkpoint:** `pip list` includes `fastapi`, `uvicorn`, and `sqlmodel`.

---

## Part 4 — Record your dependencies

Right now, the knowledge of what this project needs exists only inside your `venv` folder. That's no good — a teammate cloning your code, or you on a different laptop, would have no idea. Write it down:

```bash
pip freeze > requirements.txt
```

Open the file. It looks something like this (your version numbers will differ — that's fine):

```
annotated-types==0.8.0
anyio==4.14.2
click==8.5.0
fastapi==0.141.1
h11==0.16.0
idna==3.19
pydantic==2.13.5
pydantic_core==2.46.5
SQLAlchemy==2.0.52
sqlmodel==0.0.42
starlette==1.6.0
typing_extensions==4.16.0
uvicorn==0.52.4
```

Exact versions, so anyone can recreate your environment precisely:

```bash
pip install -r requirements.txt
```

**The rule: commit `requirements.txt`, never commit `venv/`.** The requirements file is small, it's the actual information, and it belongs to the project. The `venv` folder is hundreds of files, is specific to your machine and OS, and gets regenerated by whoever needs it. Create a file named `.gitignore` with:

```
venv/
__pycache__/
*.db
```

Re-run `pip freeze > requirements.txt` any time you install something new. It's a snapshot, not a live feed — it doesn't update itself.

**Checkpoint:** `requirements.txt` exists and lists `fastapi`, `sqlmodel`, and `uvicorn` with `==` version numbers.

---

## Part 5 — Your first FastAPI app

This is the same app you ran in class. Create a file named `main.py`:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, backend world!"}
```

Run it:

```bash
uvicorn main:app --reload
```

- `main:app` tells uvicorn where to look — the `app` object, inside `main.py`.
- `--reload` restarts the server whenever you save a change. A development convenience; never used in production.

Open **http://127.0.0.1:8000** — your JSON message. You are running a server: a live program on your own machine, listening on port 8000.

Now open **http://127.0.0.1:8000/docs** — FastAPI built an interactive documentation page for your endpoint, for free. You'll use this constantly in Part 9.

Leave the server running in this terminal. Open a **second terminal** for the remaining commands (activate the venv there too). Stop a server with `Ctrl+C`.

**Checkpoint:** both URLs load — JSON at `/`, an interactive page at `/docs`.

---

## Part 6 — Grow into a package

One file is fine for one endpoint. You're about to write five endpoints, a database connection, and a data model, and one file stops being fine fast. Time to split it up, using exactly the idea from the modules-and-packages section: **a module is one file; a package is a folder of modules.**

Build this structure:

```
project-1/
├── venv/                 <- never committed
├── requirements.txt
├── .gitignore
├── tasks.db              <- doesn't exist yet; appears on first run
├── main.py               <- entry point, starts the app
└── app/                  <- a PACKAGE
    ├── __init__.py       <- empty; marks the folder as a package
    ├── models.py         <- what a Task is
    ├── database.py       <- engine, tables, sessions
    └── routes.py         <- the five endpoints
```

```bash
mkdir app
touch app/__init__.py app/models.py app/database.py app/routes.py
```

On Windows PowerShell, `touch` doesn't exist — use `New-Item app/__init__.py` for each, or just create the files in your editor.

`__init__.py` stays empty. Modern Python doesn't strictly require it, but it's the convention you'll see in every real codebase, so build the habit now.

The point of splitting this way: each file has one job, and you can find the file you want by its name alone.

**Checkpoint:** `ls app` shows four `.py` files.

---

## Part 7 — Add the database

### Why SQLite

SQLite is a complete database that lives in a **single file on disk**. No server to install, no passwords, no configuration — the file *is* the database. That makes it perfect for learning, and it's genuinely used in production for plenty of real applications.

The important consequence: your data survives. When you stop the server, the file stays on disk with everything in it.

### The model — `app/models.py`

```python
from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    done: bool = False
```

This one small class does two jobs at once: it describes a database table *and* the shape of the JSON your API accepts and returns.

- `table=True` is what makes it a real database table rather than just a shape.
- `id: int | None` with `primary_key=True` — every row needs a unique id. It's `None` before saving because **the database assigns it**, not you.
- `title: str` — required. `done: bool = False` — optional, defaults to false.

> **Forward reference — Week 2 and Week 3.** The `class` syntax is Lecture 2. The `title: str` type-hint style, and how FastAPI uses it to validate incoming JSON, is Week 2. `SQLModel` and `Field` are Week 3. Copy it, run it, see it work — that's the whole goal today.

### The connection — `app/database.py`

```python
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
```

- **`engine`** — the object that knows how to reach your database. `sqlite:///tasks.db` says "SQLite, in a file called tasks.db, right here".
- **`echo=True`** — prints every SQL statement to your terminal. Leave it on: watching the actual SQL appear as you click around is one of the best ways to understand what's happening underneath. Turn it off for production.
- **`connect_args={"check_same_thread": False}`** — SQLite is cautious about being used from more than one thread; FastAPI legitimately does that. Required boilerplate, not something to think about.
- **`create_db_and_tables()`** — creates the tables. Safe to run every startup; it skips anything that already exists.
- **`get_session()`** — a session is one conversation with the database. Each request gets its own and it closes when the request ends.

### Wire it up — `main.py`

Replace `main.py` entirely:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

fdfdfdfd
app = FastAPI(title="Task API", lifespan=lifespan)
app.include_router(router)


@app.get("/")
def read_root():
    return {"message": "Hello, backend world!"}
```

Notice `main.py` stayed tiny. It creates the app and plugs in the routes; all the real work lives inside `app/`.

The `lifespan` function runs your table creation once, when the server starts. `@asynccontextmanager` and `async` are pure copy-now material — flagged and set aside.

The server will error until Part 8 exists, because `app/routes.py` is still empty. That's expected.

**Checkpoint:** all three files saved. Nothing to run yet.

---

## Part 8 — CRUD: the five operations

**CRUD** = Create, Read, Update, Delete. Every backend you ever write does these four things to something, and the HTTP methods map onto them directly:

| Method | Path | Does | Success code |
|--------|------|------|--------------|
| POST | `/tasks` | create a task | 201 |
| GET | `/tasks` | list all tasks | 200 |
| GET | `/tasks/{id}` | get one task | 200 (404 if missing) |
| PUT | `/tasks/{id}` | replace a task | 200 (404 if missing) |
| DELETE | `/tasks/{id}` | delete a task | 204 (404 if missing) |

Here is the whole of `app/routes.py`. Read the notes underneath before you run it.

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Task

router = APIRouter()


@router.post("/tasks", response_model=Task, status_code=201)
def create_task(task: Task, session: Session = Depends(get_session)):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/tasks", response_model=list[Task])
def list_tasks(session: Session = Depends(get_session)):
    return session.exec(select(Task)).all()


@router.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, new_data: Task, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = new_data.title
    task.done = new_data.done
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
```

**Create.** Three steps every time: `add` stages the object, `commit` writes it to disk, `refresh` reads it back. That third one matters — `refresh` is how the database-assigned `id` gets into your object. Skip it and you'd return a task with `id: null`.

**Read all.** `select(Task)` builds the query, `session.exec` runs it, `.all()` collects the rows. That's SQL's `SELECT * FROM task`, written in Python.

**Read one.** `session.get(Task, task_id)` fetches by primary key — the common case, so it gets its own shortcut. It returns `None` when nothing matches, which is why every single-item endpoint checks for `None` and raises a 404. **Returning "not found" correctly is your job, not the framework's** — without that check, a missing task would crash with a 500 and tell the client nothing useful.

**Update.** Fetch, change the fields, then the same add/commit/refresh. This is `PUT`, meaning *replace* — the client sends the complete task. Changing one field alone is `PATCH`, which you'll meet in Week 2.

**Delete.** Fetch, `session.delete`, `commit`. The function returns nothing at all, and `status_code=204` means "No Content" — success, with an empty body. There's genuinely nothing to send back after a deletion.

> **An honest simplification.** Using the `Task` model directly as the request body means a client could send its own `id` and overwrite yours. Real projects define separate models for input and output — `TaskCreate`, `TaskUpdate`, `TaskPublic`. We're using one model here to keep the moving parts down. Week 2 covers the split properly; when it does, this is the reason it exists.

**Checkpoint:** all four files saved, no typos.

---

## Part 9 — Run it and try everything

```bash
uvicorn main:app --reload
```

Watch the terminal — with `echo=True`, you'll see the `CREATE TABLE task` statement scroll past on startup. And `ls` now shows a **`tasks.db`** file that wasn't there before. That's your database.

### Through the docs page

Open **http://127.0.0.1:8000/docs**. All five endpoints are listed. For each one: click it, click **Try it out**, fill in the fields, click **Execute**, and read the response code and body.

Do this in order:

1. **POST `/tasks`** with `{"title": "Prepare lecture 2"}` → **201**, and the response has an `id`.
2. **POST** another one → note it gets the next `id`.
3. **GET `/tasks`** → both tasks come back.
4. **GET `/tasks/1`** → just the first.
5. **GET `/tasks/99`** → **404** with `{"detail": "Task not found"}`.
6. **PUT `/tasks/1`** with `{"title": "Prepare lecture 2", "done": true}` → **200**, now `done: true`.
7. **DELETE `/tasks/2`** → **204**, empty body.

### The same thing from the terminal

A browser is not the only client. Open a second terminal — this is the client–server diagram with `curl` playing the client:

```bash
curl http://127.0.0.1:8000/tasks
```

```bash
curl -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d '{"title": "Prepare lecture 2"}'
```

```bash
curl -X PUT http://127.0.0.1:8000/tasks/1 -H "Content-Type: application/json" -d '{"title": "Prepare lecture 2", "done": true}'
```

```bash
curl -i -X DELETE http://127.0.0.1:8000/tasks/2
```

That last `-i` prints the response headers, so you see the status code doing real work:

```
HTTP/1.1 204 No Content
date: Fri, 28 Aug 2026 19:56:33 GMT
server: uvicorn
```

A status line, headers, and no body at all.

### The part that actually matters

Create a couple of tasks. Then:

1. **Stop the server** with `Ctrl+C`.
2. **Start it again**: `uvicorn main:app --reload`.
3. **`curl http://127.0.0.1:8000/tasks`**

**Your tasks are still there.** That is the entire point of this project. The demo you saw in class kept its tasks in a Python dictionary, and every restart wiped them. Now they're in `tasks.db`, and they'll be there tomorrow.

Delete `tasks.db` and restart, and you're back to an empty database with the table recreated from scratch. Useful when you want a clean slate.

**Checkpoint:** data survives a restart. If it does, you've built a working backend.

---

## Part 10 — What you just copied, and when you'll understand it

Plenty here you typed without fully understanding. That was the plan. Here's the map:

| What you used | When it gets explained |
|---|---|
| `class Task(...)` — classes and objects | Week 1, Lecture 2 |
| `@app.get(...)`, `@router.post(...)` — decorators | Week 2 |
| `{task_id}` in a path, and typed function parameters | Week 2 |
| `title: str` validation, request vs. response models | Week 2 |
| `Depends()` — dependency injection | Week 2 |
| `SQLModel`, engines, sessions, `select()` | Week 3 |
| Automated tests for all five endpoints | Week 3 |
| `async` / `await` and `@asynccontextmanager` | Week 4 |
| Linting and formatting this code | Week 4 |

Keep `project-1/`. You'll come back to it.

**If you want to push further:** add a `created_at` timestamp to `Task` using the built-in `datetime` module; add `PATCH /tasks/{id}` that updates only `done`; or add `GET /tasks?done=true` to filter the list. All three are genuinely doable with what's above plus the FastAPI docs.

---

## Troubleshooting

**`command not found: python`**
Use `python3` and `pip3` instead. Common on macOS and Linux.

**PowerShell won't run `Activate.ps1`** — *"running scripts is disabled on this system"*
Windows blocks scripts by default. In PowerShell:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then activate again.

**`ModuleNotFoundError: No module named 'fastapi'`**
Your venv isn't active. Look at your prompt — no `(venv)`, that's the problem. Activate and retry. This is far and away the most common error in this guide.

**`uvicorn: command not found`**
Same cause: either the venv isn't active, or you installed the packages before activating it. Activate, re-run `pip install fastapi uvicorn sqlmodel`.

**`ERROR: [Errno 48] Address already in use`**
A server is already running on port 8000 — probably one you forgot in another terminal. Find and `Ctrl+C` it, or run on a different port:
```bash
uvicorn main:app --reload --port 8001
```

**`ModuleNotFoundError: No module named 'app'`**
Run `uvicorn` from the `project-1` folder itself, not from inside `app/`. Check with `pwd`.

**Code changes do nothing**
You left off `--reload`. Stop the server and restart it with the flag.

**`ImportError: cannot import name 'router'`**
`app/routes.py` is empty or missing its `router = APIRouter()` line. Recheck Part 8.

**`TypeError: unsupported operand type(s) for |`**
Your Python is older than 3.10, which is where `int | None` syntax arrived. Check `python --version` and upgrade.
