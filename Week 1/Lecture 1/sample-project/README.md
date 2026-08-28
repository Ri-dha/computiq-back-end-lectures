# Task Manager — Week 1 · Lecture 1 demo

A deliberately small CRUD backend. It exists to make two slides concrete:

- **Slide 2.9 — Layered architecture.** The three layers are three folders you can point at.
- **Slides 4.3 / 4.4 — Packages and project layout.** `app/` is a package of packages, and every `import` in this project is the import syntax from section 4.

There is **no database**. Data lives in a Python dictionary and disappears when you stop the server — that is Week 3's job.

---

## Running it

```bash
cd sample-project
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open **http://127.0.0.1:8000/docs** — FastAPI's interactive docs. Every endpoint below can be clicked and run from that page, which is the easiest way to demo it live.

---

## The layout

```
sample-project/
├── main.py                  <- entry point: creates the app, plugs in routes
├── requirements.txt
└── app/                     <- PACKAGE
    ├── models/task.py       <- what a task looks like
    ├── routes/tasks.py      <- PRESENTATION layer  (HTTP in, HTTP out)
    ├── services/task_service.py  <- BUSINESS LOGIC layer  (the rules)
    └── storage/task_store.py     <- DATA ACCESS layer  (the "database")
```

A request flows straight down and back up:

```
HTTP request -> routes -> services -> storage -> services -> routes -> HTTP response
```

The point to land: **`routes/` doesn't know how data is stored, and `storage/` doesn't know what HTTP is.** In Week 3, `task_store.py` gets rewritten to use a real database with SQLModel, and nothing else in the project changes.

---

## The endpoints

| Method | Path | Does | Success code |
|--------|------|------|--------------|
| GET | `/tasks` | list all tasks | 200 |
| GET | `/tasks/{id}` | get one task | 200 (404 if missing) |
| POST | `/tasks` | create a task | 201 |
| PUT | `/tasks/{id}` | replace a task | 200 (404 if missing) |
| DELETE | `/tasks/{id}` | delete a task | 204 (404 if missing) |

That table is slide 2.6 (request methods) and slide 2.7 (status codes) in working code.

---

## Trying it from the terminal

Useful if you want to show that a browser is not the only client — this is the client–server diagram with `curl` playing the client.

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
curl -i -X DELETE http://127.0.0.1:8000/tasks/1
```

The `-i` on the last one prints the response headers, so students can see `HTTP/1.1 204 No Content` with an empty body — a status code doing real work.

---

## Teaching notes

**Where this fits in the 3 hours.** Lecture 1 is deliberately procedural about FastAPI — students type `main.py`, run it, see JSON. This project is *not* meant to be typed out in class. Use it in one of two ways:

1. **End of section 2 (~1:15), as a 3-minute payoff.** Run it, open `/docs`, create and delete a task. "This is a backend. In four weeks you will have written this and more." Then close it.
2. **End of section 4 (~3:19), as the answer to "why do packages matter?"** After Exercise 2, open this project and show that `greetings/polite.py` and `app/services/task_service.py` are the same idea at different scale.

Option 2 is the stronger placement — it lands right after students have built their own package, so the structure reads as familiar rather than intimidating.

**Two questions students reliably ask:**

- *"Where did the data go?"* — It was in memory. Restarting the server wipes it. This is the honest motivation for Week 3.
- *"Why so many folders for five functions?"* — Because it isn't five functions for long. Show them `task_store.py` and ask what would have to change to swap in a real database. The answer — "only this file" — is the whole argument for layering.

**If you are running short on time**, skip this demo entirely. It reinforces; it doesn't introduce anything the objectives depend on.
