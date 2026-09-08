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

Three packages, three completely different jobs. Knowing which one does what is worth five minutes now, because when something breaks later, the error almost always comes from exactly one of them.

### fastapi — describes your API

FastAPI is where you say **what your app does**: which URLs exist, which HTTP method each one answers, and what comes back.

```python
@app.get("/tasks")        # "when someone sends GET /tasks, run this function"
def list_tasks():
    return [...]
```

That's the core idea. You write ordinary Python functions; FastAPI's job is connecting each one to a URL. You'll write five of these in Part 8.

Two things it also does for free, which is most of the reason this course uses it:

- **Validation.** You declare the shape of your data once, and FastAPI checks every incoming request against it. Send a task with a number where the title should be, and it's rejected with a `422` before your function ever runs — you don't write that check.
- **Documentation.** The `/docs` page you'll open in Part 5 is generated from your code. It cannot drift out of date, because there's nothing separate to update.

What FastAPI does **not** do is touch the network. It doesn't know what a port is and can't receive a request on its own. It's a library that sits there waiting to be called. That's what the next package is for.

*Week 2 is entirely about this package.*

### uvicorn — actually runs it

Remember the definition of a server from Lecture 1: *a running program that listens on a network port for requests and sends back responses.* **That program is uvicorn**, not FastAPI.

When a request arrives, uvicorn:

1. is listening on port 8000 and accepts the connection,
2. reads the raw HTTP text off the wire and turns it into something Python can work with,
3. hands it to your FastAPI app and gets your function's return value back,
4. turns that into a proper HTTP response — status line, headers, JSON body — and sends it.

FastAPI decides *what the answer is*. Uvicorn handles *everything about getting the question in and the answer out*. You can see the handoff in the command itself:

```bash
uvicorn main:app
```

You are handing uvicorn your `app` object and saying "run this." The two are separate on purpose: they talk through an agreed interface called **ASGI**, so you could swap uvicorn for a different ASGI server in production without changing a line of your own code. That's vocabulary to recognize, nothing you need to act on.

### sqlmodel — talks to the database

Databases speak SQL; your program speaks Python. Something has to sit in the middle. Without SQLModel you'd be writing SQL strings by hand and unpacking raw rows into dictionaries yourself:

```python
# What you'd otherwise write:
cursor.execute("INSERT INTO task (title, done) VALUES (?, ?)", (title, done))
```

With SQLModel you define one Python class and get both the database table and the JSON shape of your API from it — which is exactly what you'll do in Part 7. A tool that maps objects to database rows like this is called an **ORM** (Object-Relational Mapper).

SQLModel is built on top of two libraries you'll see in your install:

- **SQLAlchemy** — the long-established Python database toolkit. It generates the actual SQL and manages connections. SQLModel is a friendlier layer over it.
- **Pydantic** — the validation library FastAPI already uses for the checking described above.

That combination is the point: the *same* class can be a database table and a validated API model, because it's built on the tool for each. SQLModel was written by the same author as FastAPI, specifically to fit it.

*Week 3 is where this gets taught properly; you're getting an early look.*

### Confirm what landed

```bash
pip list
```

You'll see more than three packages. The extras are dependencies — packages your packages needed. `SQLAlchemy` and `pydantic` are the two just described, pulled in automatically by SQLModel; the rest belong to FastAPI and uvicorn. You don't install these yourself and you don't need to think about them.

A quick recap of the three you did install:

| Package | Its job | If it's missing, you'll see |
|---------|---------|----------------------------|
| `fastapi` | defines your endpoints and validates data | `ModuleNotFoundError: No module named 'fastapi'` |
| `uvicorn` | listens on the port and runs your app | `uvicorn: command not found` |
| `sqlmodel` | maps Python classes to database tables | `ModuleNotFoundError: No module named 'sqlmodel'` |

All three of those errors mean the same thing nine times out of ten: **the venv isn't active.** See Troubleshooting.

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

### Running on a different port

There is nothing special about 8000 — it's just uvicorn's default. Pick another with `--port`:

```bash
uvicorn main:app --reload --port 8001
```

**The URL has to change to match.** Your app is now at `http://127.0.0.1:8001` and `http://127.0.0.1:8001/docs`; the old address stops working entirely. This catches people out constantly — they change the port, then keep refreshing the old tab and conclude the server is broken.

Don't guess which port you're on. Uvicorn prints it on startup, and that line is the authority:

```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```

Two reasons you'll actually need this:

- **Something else already has port 8000.** Uvicorn refuses to start and says so:

  ```
  ERROR:    [Errno 48] error while attempting to bind on address ('127.0.0.1', 8000): address already in use
  ```

  Usually a server you forgot in another terminal. Either stop that one with `Ctrl+C`, or just move to a free port. (The error number is OS-specific — 48 on macOS, 98 on Linux, 10048 on Windows — but the wording is the same.)
- **You want two projects running at once** — this one on 8000, another on 8001. Each server needs its own port; two programs cannot listen on the same one.

Any number between 1024 and 65535 is fair game. Below 1024 needs admin rights on macOS and Linux, so avoid those.

> **Also worth knowing:** by default the server accepts connections only from your own machine. Adding `--host 0.0.0.0` lets other devices on your network reach it — useful for testing from your phone, but it does expose the app to everyone on that network. Use it deliberately, not by habit.

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

> **An honest simplification.** Using the `Task` model directly as the request body means a client could send its own `id` and overwrite yours. Real projects define separate models for input and output — `TaskCreate`, `TaskUpdate`, `TaskPublic`. We're using one model here to keep the moving parts down, so Part 9 gets you to a running API as fast as possible. **Part 11 fixes it properly** — and shows you the specific bug this version lets through.

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

## Part 10 — Routing: how a request finds your function

> **Parts 10–13 upgrade what you already have.** You have a working API — don't throw it away. These four parts replace `app/models.py` and `app/routes.py` with better versions and explain every change. Keep the server running with `--reload` and watch each step take effect.

Routing is the question "a request just arrived — which function do I call?" You answer it with a decorator:

```python
@router.get("/tasks/{task_id}")
```

That single line is a **method** (`get`) plus a **path** (`/tasks/{task_id}`). Together they identify one route. `GET /tasks` and `POST /tasks` share a path but are two entirely separate routes, because the method differs.

### Two ways to put data in a URL

You've used one already. Here is the other.

**Path parameters** name *which* thing you want. They're part of the path, in curly braces:

```python
@router.get("/tasks/{task_id}")
def get_task(task_id: int, session: Session = Depends(get_session)):
    ...
```

The name in `{}` matches the function parameter. Nothing else connects them.

**Query parameters** are everything after the `?`, and they usually *modify* a request rather than identify a thing — filters, sorting, paging. Here's the rule that surprises everyone:

> **A parameter is a query parameter simply because its name is *not* in the path.** There's no different decorator and no extra syntax. FastAPI checks the path string; anything left over is a query parameter.

Give `list_tasks` three of them:

```python
@router.get("/tasks", response_model=list[TaskPublic])
def list_tasks(
    done: bool | None = None,
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session),
):
    query = select(Task)
    if done is not None:
        query = query.where(Task.done == done)
    return session.exec(query.offset(skip).limit(limit)).all()
```

Every one has a default, which is exactly what makes them optional — `GET /tasks` still works untouched. Now these work too:

```bash
curl "http://127.0.0.1:8000/tasks?done=true"
```

```bash
curl "http://127.0.0.1:8000/tasks?skip=1&limit=2"
```

`.where()`, `.offset()` and `.limit()` build the filtering into the SQL itself. With `echo=True` on, watch your terminal — the `SELECT` statement changes as you change the URL. You are not filtering in Python; the database is doing it.

### A required query parameter

Leave the default off and the parameter becomes required. Add a search route:

```python
@router.get("/tasks/search", response_model=list[TaskPublic])
def search_tasks(q: str, session: Session = Depends(get_session)):
    query = select(Task).where(Task.title.contains(q))
    return session.exec(query).all()
```

`q` has no default, so `GET /tasks/search` with no `?q=` returns a 422 automatically.

### The ordering rule — the one that will bite you

**Put that search route *above* `get_task` in the file.** Here's why.

FastAPI matches routes top to bottom and the first match wins. `/tasks/{task_id}` matches *any* single segment after `/tasks/` — including the literal word `search`. Declare it first and `/tasks/search` never runs; FastAPI tries to read `"search"` as an `int`, fails, and returns 422 forever.

> **The rule: specific, static paths go above dynamic ones that share their prefix.** `/tasks/search` before `/tasks/{task_id}`, always.

Try it wrong on purpose — swap the two, call `/tasks/search?q=co`, read the 422, then swap them back. Two minutes, and you'll never lose an afternoon to it later.

**Checkpoint:** `?done=true` filters the list, and `/tasks/search?q=co` returns matches rather than a 422.

---

## Part 11 — Requests: what the client is allowed to send

Data reaches your function three ways, and now you've used all of them:

| Where | Looks like | Used for |
|---|---|---|
| Path parameter | `/tasks/3` | *which* resource |
| Query parameter | `/tasks?done=true` | filtering, paging, options |
| Request body | JSON sent with POST/PUT/PATCH | the actual content |

`GET` and `DELETE` carry no body — everything they need fits in the URL. `POST`, `PUT` and `PATCH` do, and that body is where validation matters most.

### The problem with using one model

Right now `Task` is doing three jobs: database table, request body, and response. Those three want different shapes:

- A client **must not** set `id` — the database assigns it.
- A client **must not** see internal fields.
- A `PATCH` needs every field optional; a `POST` does not.

One class cannot be all three. So split it.

### The split — replace `app/models.py` entirely

```python
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
```

Five classes, but only one new idea: `TaskBase` holds the common fields and the others inherit from it — the same inheritance from Week 1, Lecture 2, doing real work. `Task` adds `id` and `internal_note`; `TaskPublic` adds `id` but *not* `internal_note`.

### Why this split isn't optional

Here is the part that actually matters, and it's specific to SQLModel:

> **A model with `table=True` does not validate its data.** Constraints on `Task` are ignored at runtime. Constraints on `TaskCreate` are enforced.

Prove it to yourself. With the venv active, run `python` and paste:

```python
from app.models import Task, TaskCreate

TaskCreate(title="", priority=99)   # ValidationError — rejected
Task(title="", priority=99)         # accepted, no complaint at all
```

The second line builds a completely invalid task and SQLModel says nothing. That's why the request body must be `TaskCreate` and never `Task`. In Part 8's version, the body *was* `Task` — which is exactly the bug that callout warned you about.

### PATCH — updating one field

`PUT` replaces the whole task, so the client must send every field. `PATCH` changes only what's provided:

```python
@router.patch("/tasks/{task_id}", response_model=TaskPublic)
def patch_task(task_id: int, new_data: TaskUpdate, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    updates = new_data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(task, field, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

`exclude_unset=True` is the whole trick: it returns only the fields the client actually sent. Without it, every omitted field would come back as `None` and you'd wipe the task's title by trying to tick its checkbox.

```bash
curl -X PATCH http://127.0.0.1:8000/tasks/2 -H "Content-Type: application/json" -d '{"done": true}'
```

The title and priority come back unchanged.

**Checkpoint:** `Task(title="")` is accepted in the Python shell while `TaskCreate(title="")` raises, and `PATCH` with only `{"done": true}` leaves the other fields alone.

---

## Part 12 — Responses: what the client is allowed to see

`response_model` shapes what goes *out*, independently of what your function returns. Your routes already return whole `Task` objects — including `internal_note`. Declaring `response_model=TaskPublic` strips anything not on `TaskPublic` before it leaves the building.

Here is the complete `app/routes.py`. Every route now declares both a `response_model` and, where it isn't 200, a `status_code`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Task, TaskCreate, TaskPublic, TaskUpdate

router = APIRouter()


@router.post("/tasks", response_model=TaskPublic, status_code=201)
def create_task(new_task: TaskCreate, session: Session = Depends(get_session)):
    task = Task.model_validate(new_task)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/tasks", response_model=list[TaskPublic])
def list_tasks(
    done: bool | None = None,
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session),
):
    query = select(Task)
    if done is not None:
        query = query.where(Task.done == done)
    return session.exec(query.offset(skip).limit(limit)).all()


# Static path FIRST -- see the ordering rule in Part 10.
@router.get("/tasks/search", response_model=list[TaskPublic])
def search_tasks(q: str, session: Session = Depends(get_session)):
    query = select(Task).where(Task.title.contains(q))
    return session.exec(query).all()


@router.get("/tasks/{task_id}", response_model=TaskPublic)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=TaskPublic)
def update_task(task_id: int, new_data: TaskCreate, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = new_data.title
    task.done = new_data.done
    task.priority = new_data.priority
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.patch("/tasks/{task_id}", response_model=TaskPublic)
def patch_task(task_id: int, new_data: TaskUpdate, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    updates = new_data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(task, field, value)
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

One line is new and worth naming: `Task.model_validate(new_task)` converts the validated `TaskCreate` into a `Task` the database can store. The client's data has already been checked by this point; this just moves it into the table's shape.

### Status codes, and why each one

| Route | Code | Because |
|---|---|---|
| `POST /tasks` | **201** Created | something new exists that didn't before |
| `GET`, `PUT`, `PATCH` | **200** OK | here is the thing you asked for |
| `DELETE` | **204** No Content | it worked, and there's nothing left to describe |
| bad shape or type | **422** | the request never made sense |
| no such task | **404** | the request made sense; the task doesn't exist |

**Checkpoint:** no response anywhere contains `internal_note`, and `POST` answers 201 rather than 200.

---

## Part 13 — Validation: two kinds of error

Look back at `models.py`. There is not one `if` statement checking user input — and yet an empty title is impossible. That's `Field()`:

```python
title: str = Field(min_length=1, max_length=100)
priority: int = Field(default=3, ge=1, le=5)
```

`ge` is greater-or-equal, `le` is less-or-equal. Break any of them and FastAPI answers 422 before your function's first line runs.

### Reading a 422

```bash
curl -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d '{"title": "Nope", "priority": 10}'
```

```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "priority"],
      "msg": "Input should be less than or equal to 5",
      "input": 10
    }
  ]
}
```

**Read `loc` first.** It names exactly where the problem is: `["body", "priority"]` means the `priority` field of the request body. You'll see `["query", "q"]` for a missing search term and `["path", "task_id"]` for `/tasks/abc`. `msg` then tells you what rule broke.

### 422 or 404? They come from opposite places

This distinction confuses nearly everyone, and it's simple once stated:

- **422 — nobody wrote it.** The request's shape or type was wrong, so Pydantic rejected it at the door. Nothing was looked up; your function never ran.
- **404 — you wrote it.** `raise HTTPException(status_code=404, ...)` is a decision your code made after checking a rule Pydantic cannot know: *does task 999 exist?*

`GET /tasks/abc` gives 422 because `abc` can never be a task id. `GET /tasks/999` gives 404 because `999` is a perfectly valid id that happens to match nothing. **You have to get past validation to earn a 404.**

### A trap worth stepping in once

Constraints do **not** follow a class around. `TaskUpdate` doesn't inherit from `TaskBase`, so it needs its own copy of every rule. Delete the constraints from `TaskUpdate` and try:

```bash
curl -X PATCH http://127.0.0.1:8000/tasks/2 -H "Content-Type: application/json" -d '{"priority": 99}'
```

You get **500 Internal Server Error**, not 422. The chain: `TaskUpdate` accepts 99 → `Task` is a table model, so it doesn't validate either → 99 goes into the database → `TaskPublic` *does* have `le=5`, so FastAPI can't build the response and raises `ResponseValidationError`.

A 500 always means your code broke, never that the client sent something bad. Seeing one here is a reliable sign a constraint is missing on an input model. Put them back.

**Checkpoint:** an empty title and `priority: 10` both return 422 with a readable `loc`, and `/tasks/999` returns 404.

---

## Part 14 — What you just copied, and when you'll understand it

Plenty here you typed without fully understanding. That was the plan. Here's the map:

Some of it you've now covered:

| What you used | Where it was explained |
|---|---|
| `class Task(...)` — classes, inheritance | Week 1, Lecture 2 |
| Routing, path and query parameters | Part 10 |
| Request bodies, input vs. output models | Part 11 |
| `response_model` and status codes | Part 12 |
| `Field()` constraints, 422 vs. 404 | Part 13 |

And some is still ahead:

| What you used | When it gets explained |
|---|---|
| `@app.get(...)` — how decorators actually work | Week 2 |
| `Depends()` — dependency injection | Week 2 |
| Nested models, enums, custom validators | Week 2, Lecture 2 |
| `SQLModel` internals, engines, sessions, `select()` | Week 3 |
| Automated tests for all seven endpoints | Week 3 |
| `async` / `await` and `@asynccontextmanager` | Week 4 |
| Linting and formatting this code | Week 4 |

Keep `project-1/`. You'll come back to it.

**If you want to push further:** add a `created_at` timestamp using the built-in `datetime` module; add `?sort=priority` to the list route; return a proper 409 when someone creates a task whose title already exists; or make `/tasks/search` case-insensitive and search descriptions too. All four are doable with what's above plus the FastAPI docs.

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

**`ERROR: [Errno 48] error while attempting to bind on address ... address already in use`**
A server is already running on that port — probably one you forgot in another terminal. Find and `Ctrl+C` it, or run on a different port:
```bash
uvicorn main:app --reload --port 8001
```
Then use `http://127.0.0.1:8001` for everything that follows. See "Running on a different port" in Part 5.

**`ModuleNotFoundError: No module named 'app'`**
Run `uvicorn` from the `project-1` folder itself, not from inside `app/`. Check with `pwd`.

**Code changes do nothing**
You left off `--reload`. Stop the server and restart it with the flag.

**`ImportError: cannot import name 'router'`**
`app/routes.py` is empty or missing its `router = APIRouter()` line. Recheck Part 8.

**`TypeError: unsupported operand type(s) for |`**
Your Python is older than 3.10, which is where `int | None` syntax arrived. Check `python --version` and upgrade.

**`/tasks/search` returns 422 instead of results**
`GET /tasks/{task_id}` is declared above it, so `"search"` is being read as a task id. Move the search route above it — the ordering rule in Part 10.

**`500 Internal Server Error` after a PATCH or PUT**
Almost always a missing constraint on an input model, letting a bad value reach the database that `TaskPublic` then refuses to serialize. Check that `TaskUpdate` carries the same `Field(...)` rules as `TaskBase`. See the end of Part 13.

**Every field comes back `null` after a PATCH**
You dropped `exclude_unset=True` from `model_dump()`, so unsent fields were treated as explicit `None` and overwrote real data. Part 11 has the working version.
