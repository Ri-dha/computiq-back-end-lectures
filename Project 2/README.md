# Project 2 — A Book Store API with Users, Logins and Roles

A step-by-step walkthrough. You start with an empty folder and finish with a book store backend where people sign up, log in, and are allowed to do different things depending on who they are: **customers** buy books, **staff** run the catalogue, and **admins** manage everyone.

Most of this guide is about the part tutorials usually rush — **users, passwords, logins and permissions** — because that's where a small mistake quietly becomes a security hole. The book store itself is built on top of that foundation in Parts 12 and 13.

**What this builds on.** Week 2 · Lecture 2 built a Book Store API with `Genre(str, Enum)`, `@field_validator`, `BaseSettings` and a `routers/` package. This guide uses every one of those for real. Lecture 2 calls its request and response classes *schemas*; this guide calls them **DTOs**, and Part 4 explains what that means and why they matter. It also goes past the syllabus in two places, and says so where it happens: the database is Week 3's topic (Project 1 already gave you an early look), and authentication isn't a scheduled lecture in this course at all — this guide is where it lives.

**How to use this.** Same rules as Project 1. Type the code where you can rather than pasting it. Every part ends with a **Checkpoint** — don't move on until yours matches, because in auth code a step that quietly failed looks exactly like a step that worked. There's a Troubleshooting section at the end.

---

## Part 0 — Two words you must not mix up

**Authentication** asks *who are you?* Logging in is authentication. When it fails, the answer is **401 Unauthorized** — a famously bad name, because it really means *unauthenticated*: "I don't know who you are."

**Authorization** asks *what are you allowed to do?* It only makes sense once we already know who you are. When it fails, the answer is **403 Forbidden**: "I know exactly who you are, and the answer is no."

| | Question | Fails with | For example |
|---|---|---|---|
| **Authentication** | Who are you? | **401** | no token, a wrong password, an expired token |
| **Authorization** | Are you allowed? | **403** | a customer trying to delete a book |

If that split feels familiar, it should — it's the same shape as 422 vs. 404 in Project 1. One is about the request itself; the other is a rule your code decides.

### The roles

Everyone who signs up is a **customer**. Staff and admins are made by an admin — never by signing up.

| What | Not logged in | customer | staff | admin |
|---|:---:|:---:|:---:|:---:|
| Browse books | ✅ | ✅ | ✅ | ✅ |
| Place orders, see your own orders | | ✅ | ✅ | ✅ |
| Add and edit books | | | ✅ | ✅ |
| See every order, change order status | | | ✅ | ✅ |
| Delete books | | | | ✅ |
| Change roles, disable accounts | | | | ✅ |

### Three rules the whole project follows

1. **Never store a password.** Store a *hash* of it. (Part 6)
2. **Never let the client decide what the server should.** Not an `id`, not a `user_id` in the body, not a `role` in the request. Ids come from *your* database, identity from a token *you* signed, permissions from *your* records. (Parts 4, 5, 7, 8 and 13)
3. **Check permissions on the server, on every request.** Hiding a button in a website is not security — anyone can send the request without the button. (Part 10)

**Checkpoint:** without looking, you can say which status a logged-in customer gets for trying to delete a book (403), and which one a logged-out visitor gets for the same request (401).

---

## Part 1 — Set up the project

Create the folder and the virtual environment, exactly as in Project 1:

```bash
mkdir project-2 && cd project-2
```

```bash
python -m venv venv
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

**Windows (PowerShell):**

```bash
venv\Scripts\Activate.ps1
```

Now install everything, **with the quotes exactly as written**:

```bash
pip install fastapi uvicorn sqlmodel pydantic-settings email-validator "pwdlib[argon2]" pyjwt python-multipart
```

> **The quotes matter.** Without them, zsh — the default shell on macOS — reads the square brackets as a filename pattern and stops with `zsh: no matches found: pwdlib[argon2]`. The quotes are harmless in every other shell, so just always use them.

Seven packages beyond Project 1's. Here's what each one is for:

| Package | What it does here | Where it comes from |
|---|---|---|
| `fastapi`, `uvicorn` | the framework and the server | Project 1, Part 3 |
| `sqlmodel` | database tables written as Python classes | Project 1 · taught in Week 3 |
| `pydantic-settings` | reads configuration and secrets from a `.env` file | Week 2 · Lecture 2, §3.4 |
| `email-validator` | makes Pydantic's `EmailStr` type work | new |
| `pwdlib[argon2]` | turns passwords into safe hashes with the Argon2 algorithm | new — Part 6 |
| `pyjwt` | creates and checks login tokens | new — Part 7 |
| `python-multipart` | lets FastAPI read form data, which is what a login form sends | new — Part 9 |

Two naming traps, before they catch you: the package is called `pyjwt` but in code you write `import jwt`. And a *different*, unrelated package called plain `jwt` also exists — `pip install jwt` gets you the wrong one.

Record your dependencies:

```bash
pip freeze > requirements.txt
```

Create a file named `.gitignore`:

```
venv/
__pycache__/
*.db
.env
```

**`.env` is new on that list, and it is the most important line in the file.** In Part 3 it will hold the secret key that signs every login token. Commit it once, and anyone who can read your repository can log in as any user — including an admin.

**Checkpoint:** `(venv)` in your prompt, and `requirements.txt` lists `fastapi`, `pwdlib`, `argon2-cffi`, `PyJWT` and `python-multipart`.

---

## Part 2 — Lay out the folders

This is Lecture 2's project layout from §4.3 — a `routers/` package, with the data classes kept apart from the routes — placed inside an `app/` package the way Project 1 did it. Lecture 2 keeps all its data classes in one `schemas.py`; here they're split by direction into a `dtos/` package, which Part 4 explains. It's more files than Project 1, because auth has more separate jobs:

```
project-2/
├── venv/
├── .env                  <- your secret key (never committed)
├── .gitignore
├── requirements.txt
├── bookstore.db          <- appears on first run
├── main.py               <- creates the app, plugs in the routers
├── create_admin.py       <- makes the very first admin (Part 10)
└── app/
    ├── __init__.py
    ├── config.py         <- settings, read from .env
    ├── database.py       <- the engine and sessions
    ├── enums.py          <- Role, Genre, OrderStatus
    ├── models.py         <- the database tables (entities)
    ├── security.py       <- password hashing and tokens
    ├── dependencies.py   <- "who is calling?" and "are they allowed?"
    ├── dtos/
    │   ├── __init__.py
    │   ├── requests.py   <- what a client may SEND
    │   └── responses.py  <- what a client may SEE
    └── routers/
        ├── __init__.py
        ├── auth.py       <- sign up, log in, who am I
        ├── users.py      <- admin: roles and accounts
        ├── books.py      <- the catalogue
        └── orders.py     <- buying books
```

```bash
mkdir -p app/routers app/dtos
```

```bash
touch main.py create_admin.py app/__init__.py app/config.py app/database.py app/enums.py app/models.py app/security.py app/dependencies.py
```

```bash
touch app/dtos/__init__.py app/dtos/requests.py app/dtos/responses.py
```

```bash
touch app/routers/__init__.py app/routers/auth.py app/routers/users.py app/routers/books.py app/routers/orders.py
```

On Windows PowerShell, `touch` doesn't exist and `-p` isn't needed: run `mkdir app\routers` and `mkdir app\dtos`, then create the files from your editor.

> **Expect red underlines for a while.** Until a file has code in it, your editor will flag every import that points at it — `Cannot find reference 'router'` and similar. That's not a typo, it's an empty file. Each one disappears when you reach the part that fills it in.

**Checkpoint:** `ls app app/dtos app/routers` shows every file in the tree above.

---

## Part 3 — Settings, and the key that signs every login

In Part 7 the API will hand out login tokens, and each one is signed with a **secret key**. The signature is what makes a token impossible to forge. That makes the key the most sensitive value in the whole project: **anyone who has it can create a valid token for any user, including an admin**, without knowing a single password.

So it gets three kinds of care: it's long and random, it never appears in your code, and it never gets committed.

Generate one:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

That prints 64 random characters. Create a file named `.env` in the `project-2` folder and paste yours in:

```
SECRET_KEY=paste-your-64-characters-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=false
```

Now **`app/config.py`**:

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Without this line, BaseSettings only reads real environment variables
    # and silently ignores your .env file.
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "Book Store API"
    debug: bool = False
    database_url: str = "sqlite:///./bookstore.db"

    # No default, on purpose: the app refuses to start without a real key.
    secret_key: str = Field(min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()
```

This is `BaseSettings` from Lecture 2, §3.4, with three details that matter for security:

- **`model_config = SettingsConfigDict(env_file=".env")` — don't skip this line.** The `Settings` example on the lecture slide leaves it out, and without it `BaseSettings` reads only real environment variables and *silently ignores* your `.env` file. The app then fails with a missing `secret_key` while the file sits right there, correct. Nothing was reading it.
- **`secret_key` has no default.** A default key would be a key written into the code, visible to everyone, and identical on every copy of the project. With no default, the app refuses to start until you give it a real one.
- **`Field(min_length=32)`** stops someone setting `SECRET_KEY=secret` to get past that. A short key can be guessed by trying possibilities.

Names match case-insensitively: `secret_key` in the class is filled from `SECRET_KEY` in the file. And a real environment variable always beats `.env` — which is how a production server supplies its own key without any file at all.

**See it refuse to start.** Temporarily rename `.env` to something else, then run:

```bash
python -c "from app.config import settings"
```

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
secret_key
  Field required [type=missing, input_value={}, input_type=dict]
```

That's what you want: a loud failure at startup instead of an app quietly running with no protection. Put the name back. (Set `SECRET_KEY=secret` and you'll get `String should have at least 32 characters` instead.)

> **If your key ever leaks, generate a new one.** Every token signed with the old key stops working instantly and everyone has to log in again — which is exactly what you want after a leak. Passwords keep working, because password hashes don't use the secret key at all.

**Checkpoint:** this prints `Book Store API`:

```bash
python -c "from app.config import settings; print(settings.app_name)"
```

---

## Part 4 — DTOs: what comes in, and what goes out

One idea shapes every file from here on, so it comes before any more code.

### What a DTO is

A **DTO** — a *Data Transfer Object* — is a class whose only job is to describe data **crossing the edge of your API**: coming in with a request, or going out with a response. It holds no database logic and no business rules. Just field names, types and validation.

You've written them already. Lecture 2's `BookCreate` and Project 1's `TaskCreate` and `TaskPublic` are DTOs. FastAPI's documentation — and Lecture 2 — call them *schemas*; most other frameworks, such as Spring in Java, ASP.NET and NestJS, call them DTOs. Same idea, two names. This project says "DTO", and puts the direction into every name so the two kinds can never be confused:

| | Request DTO | Response DTO |
|---|---|---|
| Describes | what a client is **allowed to send** | what a client is **allowed to see** |
| Used in a route as | a parameter: `new_book: BookCreateRequest` | `response_model=BookResponse` |
| Lives in | `app/dtos/requests.py` | `app/dtos/responses.py` |
| Named like | `BookCreateRequest`, `RoleUpdateRequest` | `BookResponse`, `UserResponse` |

One thing that is **not** a DTO: a database table. `User`, `Book` and `Order` in Part 5 describe what is *stored*, and are called **entities**. A DTO is the part of an entity that the outside world is allowed to touch — never the entity itself:

```
client  ──JSON──▶  request DTO   ──▶  your code  ──▶  entity (table)  ──▶  database
client  ◀──JSON──  response DTO  ◀──  your code  ◀──  entity (table)  ◀──  database
```

### Why use DTOs instead of the table everywhere

Project 1 did use one class for everything at first (Part 8), and Part 11 had to take it apart again. Here is why — and every one of these reasons turns up somewhere in this project:

1. **Security on the way in.** A request DTO is an allow-list: any field it doesn't declare is thrown away before your code sees it. Use the `User` table as the sign-up body instead, and a client could send `"role": "admin"` or `"id": 1` straight into your database. That attack has a name — **mass assignment** — and it's one of the most common API vulnerabilities there is.
2. **Security on the way out.** A response DTO is an allow-list too. The `User` table has a `hashed_password` column and `UserResponse` doesn't, so the hash can't appear in a response — even when a route returns the whole `User` object.
3. **Different operations need different rules.** Adding a book requires a title; changing its price shouldn't. `BookCreateRequest` makes the fields required and `BookUpdateRequest` makes them all optional. One class can't be both.
4. **The database can change without breaking clients.** Rename a column, add an internal field, split a table — as long as the DTOs stay the same, nothing a client depends on moves.
5. **Validation always runs.** Project 1, Part 11 showed that SQLModel tables with `table=True` skip validation. These DTOs are plain Pydantic `BaseModel`s, so every request is checked, every time.
6. **The documentation is exact.** `/docs` lists every DTO by name, so whoever builds a frontend sees precisely what each route accepts and what it returns.

The cost is some repetition: `BookCreateRequest`, `BookResponse` and the `Book` table share several fields. That's deliberate — each one is free to change for its own reason.

### The enums — `app/enums.py`

```python
from enum import Enum


class Role(str, Enum):
    customer = "customer"
    staff = "staff"
    admin = "admin"


class Genre(str, Enum):
    fiction = "fiction"
    nonfiction = "nonfiction"
    poetry = "poetry"


class OrderStatus(str, Enum):
    pending = "pending"
    shipped = "shipped"
    cancelled = "cancelled"
```

`Genre` is Lecture 2's, exactly. `Role` is the same idea: a role can only ever be one of three strings, so `?role=superuser` is rejected with a 422 before any of your code runs. `OrderStatus` is used in Part 13.

They get a file of their own because two different layers use them — the DTOs here, and the entities in Part 5. Put them in either one, and the other would have to import from it.

### Request DTOs — `app/dtos/requests.py`

This is the first part of the file. Parts 12 and 13 add to the bottom of it.

```python
"""Request DTOs: what a client is ALLOWED to send.

Any field not declared here is thrown away before your code sees it. That is
why none of these has an `id`, a `role` for sign-up, a `user_id` or a price.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.enums import Genre, OrderStatus, Role


# ----------------------------------------------------------------- users

class UserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def username_is_simple(cls, value):
        if not value.replace("_", "").isalnum():
            raise ValueError("may only contain letters, numbers and underscores")
        return value.lower()

    @field_validator("email")
    @classmethod
    def email_is_lowercase(cls, value):
        return value.lower()

    @field_validator("password")
    @classmethod
    def password_has_letter_and_number(cls, value):
        has_letter = any(char.isalpha() for char in value)
        has_number = any(char.isdigit() for char in value)
        if not (has_letter and has_number):
            raise ValueError("must contain at least one letter and one number")
        return value


class RoleUpdateRequest(BaseModel):
    role: Role


class ActiveUpdateRequest(BaseModel):
    is_active: bool
```

**`UserCreateRequest`** — what someone sends to sign up — is Lecture 2 §3.3's validators doing real work:

- **`username`** — `Field` handles the length. The validator handles what `Field` can't express: *only letters, numbers and underscores*. It also lowercases, so `Amina` and `amina` can never become two different accounts.
- **`email`** — `EmailStr` is real email checking, from the `email-validator` package. The lecture wrote a hand-rolled `"@" in value` check to show how validators work; this is what you'd use for real. It lowercases the domain but keeps the case of the part before `@`, so the validator lowercases the whole thing.
- **`password`** — 8 to 128 characters, and the validator requires a letter and a number. The upper limit matters too: without it, someone could send a megabyte-long "password" and make your server spend ages hashing it.

> **The fields that aren't there.** `UserCreateRequest` has no `role` and no `id`. A sign-up request containing `"role": "admin"` or `"id": 1` has those lines thrown away before your code runs. Those two absences are the most important security decisions in this file — Part 9 proves the first, and Part 14 the second.

**`RoleUpdateRequest`** and **`ActiveUpdateRequest`** are the tiny request bodies for the admin actions in Part 11. (`Genre` and `OrderStatus` are imported now and used in Parts 12 and 13.)

> **An honest note on password rules.** "At least one letter and one number" is a teaching rule. Length does far more for a password's strength than character rules do, and serious systems also reject passwords already known from data breaches. It's the validator mechanism that matters here, not this particular rule.

### Response DTOs — `app/dtos/responses.py`

Also the first part of its file:

```python
"""Response DTOs: what a client is ALLOWED to see.

Routes use these as their response_model, so anything not declared here --
like a password hash -- is stripped out before the response leaves.
"""

from datetime import datetime

from pydantic import BaseModel

from app.enums import Genre, OrderStatus, Role


# ----------------------------------------------------------------- users

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: Role
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

- **`UserResponse`** is everything that's safe to show about a user. Every route that returns a user uses it as its `response_model`, so the hash stored in the database can't leak out, even by accident.
- **`TokenResponse`** is the shape of a login response. The names `access_token` and `token_type` aren't our choice — they come from the OAuth2 standard, and the `/docs` login button depends on them.
- **Every response DTO for something stored has an `id`, and no request DTO does.** A client needs an id to refer to things later — `GET /books/3` — but never gets to choose one. Part 5 shows where ids come from.

(`datetime`, `Genre` and `OrderStatus` are imported now and used in Parts 12 and 13.)

### Try it

In the Python shell — run `python` with your venv active:

```python
from app.dtos.requests import UserCreateRequest
UserCreateRequest(username="Amina", email="Amina@Example.com", password="reads4ever", role="admin", id=1)
```

```
UserCreateRequest(username='amina', email='amina@example.com', password='reads4ever')
```

Lowercased and validated — and the `role` and `id` you tried to sneak in are simply gone. That's the allow-list at work.

```python
UserCreateRequest(username="amina", email="amina@example.com", password="password")
```

That one raises a `ValidationError` ending in `Value error, must contain at least one letter and one number`.

**Checkpoint:** the first call comes back lowercase with no `role` and no `id`, and the second is rejected.

---

## Part 5 — The database tables

**`app/database.py`**:

```python
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False},
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

The same as Project 1, except the database address and `echo` now come from your settings. `echo` is off by default for a reason: turn `DEBUG=true` on and every SQL statement gets printed — including the `INSERT` that stores each password hash. Useful when you're debugging, but not something to leave on.

**`app/models.py`**:

```python
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from app.enums import Genre, OrderStatus, Role


class User(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}  # never reuse a deleted id

    id: int | None = Field(default=None, primary_key=True)  # set by the database
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: Role = Role.customer
    is_active: bool = True


class Book(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}

    id: int | None = Field(default=None, primary_key=True)
    title: str
    author: str
    genre: Genre = Genre.fiction
    price: float
    stock: int = 0


class Order(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    book_id: int = Field(foreign_key="book.id", index=True)
    quantity: int
    total_price: float
    status: OrderStatus = OrderStatus.pending
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

**Entities, not DTOs.** These three classes describe what's *stored*. None of them is ever a request body or a `response_model` — that's the DTOs' job, from Part 4. Project 1, Part 11 showed that `table=True` models don't validate their data; because no request ever lands in an entity directly, that trap can't happen here. Every request passes through a request DTO first.

**`User`**, line by line:

- `unique=True` — the database itself refuses a second account with the same username or email, even if some future code forgets to check. `index=True` makes looking a user up by username fast, which every single login does.
- `hashed_password` — the column is named for what it holds. There is no column that could hold a real password.
- `role` defaults to `customer`.
- `is_active` lets an admin **disable** an account without deleting it. Deleting would break every order that points at that user.

### Where ids come from

Look at the top of each table. **Your code never picks an id** — the database does:

```python
__table_args__ = {"sqlite_autoincrement": True}
id: int | None = Field(default=None, primary_key=True)
```

- **`primary_key=True`** makes `id` the column that identifies each row. No two rows can share one.
- **`int | None` with a default of `None`** — a brand-new `Book(...)` object has `id = None`, because it hasn't been saved and nobody has picked a number yet.
- **The database picks it on `commit`:** 1, 2, 3, and so on. `session.refresh(...)` then reloads the saved row, so your Python object holds exactly what the database has — new id included. (SQLAlchemy would quietly reload it the next time the object is read anyway; `refresh` makes that step visible instead of hidden, which is why every create route here keeps it.)
- **`sqlite_autoincrement=True` means an id is never used twice.** `__table_args__` is a special class attribute that SQLModel reads when it creates the table. Without this line, SQLite hands the id of the *most recently deleted* row to the next new one: add books 1, 2 and 3, delete book 3, and the next book is 3 again — so anyone still holding a link to the old book 3 silently gets a different book. With it, the next book is 4, whatever was deleted.

Three rules keep ids trustworthy, and this project follows all three:

| Rule | Where it happens |
|---|---|
| No request DTO has an `id` field | `app/dtos/requests.py` — a client-sent `"id"` is thrown away |
| The database assigns the id on `commit` | every create route, followed by `refresh` |
| An id is never reused | `sqlite_autoincrement=True` on every table |

> **Why not work out the next id yourself?** Something like `len(books) + 1` breaks the first time a row is deleted: with books 1, 2 and 4 left, it produces 4 again — a duplicate. The database already solves this properly, including when two requests arrive at the same moment.

> **An id in a URL is a different thing.** `GET /books/3`, or `"book_id": 3` inside an order, *refers to* a book that already exists. It doesn't create anything or choose a new id. A client can point at any id it likes — whether they're allowed to see what's there is what Parts 10 and 13 decide.

`Book` and `Order` are explained in Parts 12 and 13. Two small things now: `foreign_key="user.id"` records that `user_id` points at a row in the `user` table (SQLite doesn't actually enforce that by default — Week 3 covers relationships properly). And `default_factory` takes a *function*, here a lambda from Week 1 · Lecture 2, which is called fresh for each new order, so every order gets its own timestamp.

**Checkpoint:** both files saved. Nothing to run yet.

---

## Part 6 — Storing passwords safely

Here's why this matters so much. Databases leak — through bugs, stolen backups, a laptop left on a train. And people reuse passwords, so a leaked book store password is very often someone's email password too.

The fix is to never store the password at all. You store a **hash** of it:

- **A hash is one-way.** You can turn a password into a hash, but there is no way to turn a hash back into a password. To log someone in, you don't "decrypt" anything — you check whether the password they just typed matches the stored hash.
- **It is not encryption.** Encryption can be reversed with a key, and whoever gets that key gets every password at once.
- **Every hash is salted.** A random value is mixed in and stored inside the hash itself. Hash the same password twice and you get two completely different results, so an attacker can't spot everyone who used `password1`.
- **It is slow on purpose.** One check takes a few tens of milliseconds. For one login, nobody notices. For an attacker trying billions of guesses against a stolen database, that slowness is the whole defence.

And **never write your own.** Use a library built by people who study this: `pwdlib` with **Argon2**, the algorithm that won the international Password Hashing Competition.

**`app/security.py`** — the first half. Part 7 adds the rest.

```python
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import settings

password_hash = PasswordHash.recommended()

# A real hash of a throwaway password. When a login names a user who does not
# exist, we still check against this, so that case takes as long as a wrong
# password does -- see Part 8.
DUMMY_HASH = password_hash.hash("dummy-password-for-timing")


def hash_password(password):
    return password_hash.hash(password)


def verify_password(password, hashed_password):
    return password_hash.verify(password, hashed_password)

```

`PasswordHash.recommended()` picks Argon2 with current safe settings, so you never have to choose the numbers yourself. `DUMMY_HASH` gets explained in Part 9, where it's used. (`jwt`, `datetime` and `settings` are imported now but first used in Part 7.)

See the salt for yourself — in the Python shell:

```python
from app.security import hash_password, verify_password
first = hash_password("reads4ever")
second = hash_password("reads4ever")
first
```

```
'$argon2id$v=19$m=65536,t=3,p=4$...'
```

The hash says which algorithm and settings made it, then carries the salt and the result. Now:

```python
first == second
verify_password("reads4ever", first)
verify_password("reads4everr", first)
```

`False`, `True`, `False`. The same password produced two different hashes, both of them still verify, and one wrong letter fails.

**Checkpoint:** `first == second` is `False`, and `verify_password` accepts the right password and refuses the wrong one.

---

## Part 7 — Tokens: how the API remembers you logged in

HTTP forgets everything between requests. Every request arrives as if from a stranger. You could make the client send the password with *every* request — but then the password is flying around constantly, and you'd be running a deliberately slow hash on every single call.

Instead: **log in once, get a token, and send the token with each request** in a header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjox...
```

The token is a **JWT** — a JSON Web Token. It is three chunks of text separated by dots: a header, a payload, and a signature.

- **The payload is readable by anyone.** It's encoded, not encrypted — you'll decode one yourself in Part 9. **Never put anything secret in a token.**
- **The signature is what makes it trustworthy.** It's calculated from the payload using your `SECRET_KEY`. Change a single character of the payload and the signature no longer matches, so the token is rejected. Only someone who holds the key can make a token that passes.

Our payload holds exactly two things: `sub` (the "subject" — which user this is, as their id) and `exp` (when it expires). No role, no email. Part 8 explains why leaving the role out is deliberate.

**`app/security.py`** — add this to the bottom:

```python
def create_access_token(user_id):
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def read_user_id_from_token(token):
    """Return the user id inside a valid token, or None for anything else."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub"]},
        )
        return int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError):
        return None
```

- **`create_access_token`** builds the payload and signs it. The id is stored as a string, because the JWT standard says `sub` is a string.
- **`algorithms=[settings.algorithm]`** is a list of algorithms you're willing to accept, and you must always pass it. A token's own header says which algorithm it uses, and without this list an attacker could send a token that claims `"alg": "none"` — no signature at all. This project's tests forge exactly that token, and it's rejected.
- **`options={"require": ["exp", "sub"]}`** refuses a token that is missing either field, even if it's correctly signed. A token with no expiry would work forever.
- **Every failure returns `None`** — expired, tampered with, signed by a different key, or plain garbage. Whoever calls this function only has one case to handle.

**Checkpoint:** in the Python shell —

```python
from app.security import create_access_token, read_user_id_from_token
token = create_access_token(7)
read_user_id_from_token(token)
read_user_id_from_token(token + "x")
```

— gives `7`, then `None`. One extra character and the token is worthless.

---

## Part 8 — Finding out who is calling

**`app/dependencies.py`** — the first half. Part 10 adds the rest.

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.database import get_session
from app.models import User
from app.security import read_user_id_from_token

# tokenUrl tells the /docs page where to send the login form.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    not_authenticated = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = read_user_id_from_token(token)
    if user_id is None:
        raise not_authenticated

    # Look the user up on EVERY request instead of trusting a role written
    # into the token. A demoted or disabled user loses access immediately.
    user = session.get(User, user_id)
    if user is None:
        raise not_authenticated
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    return user

```

- **`OAuth2PasswordBearer`** reads the `Authorization: Bearer ...` header. If the header is missing, it replies `401 Not authenticated` by itself, before your code runs. `tokenUrl` tells the `/docs` page where the login form is — that's what makes its **Authorize** button work.
- **`get_current_user` is a dependency.** Any route that asks for `Depends(get_current_user)` now requires a login: FastAPI runs this function first, and if it raises, the route never runs at all.
- **Three ways to be turned away.** A token that doesn't check out gets **401**. A valid token for a user who no longer exists also gets **401**. A valid token for a *disabled* account gets **403** — we know exactly who this is; they're just not allowed in.
- **`WWW-Authenticate: Bearer`** is required by the HTTP standard on a 401: it tells the client *how* it's supposed to authenticate.

### Why look the user up on every request

This is why the token contains no role.

Suppose the token said `"role": "staff"`. You demote that person — and nothing happens. Their token still says staff and stays valid until it expires, so they keep staff powers for up to half an hour. Disabling a compromised account would be just as useless.

Reading the role from the database on every request means **a change takes effect on the very next request**. The cost is one lookup by primary key, which is about the cheapest thing a database can do. Part 14 demonstrates this: a demoted user's *existing* token loses its powers immediately.

**Checkpoint:** file saved. It gets used in the next part.

---

## Part 9 — Sign up, log in, and see yourself

**`app/routers/auth.py`**:

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import get_current_user
from app.dtos.requests import UserCreateRequest
from app.dtos.responses import TokenResponse, UserResponse
from app.enums import Role
from app.models import User
from app.security import DUMMY_HASH, create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(new_user: UserCreateRequest, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.username == new_user.username)).first():
        raise HTTPException(status_code=409, detail="Username is already taken")
    if session.exec(select(User).where(User.email == new_user.email)).first():
        raise HTTPException(status_code=409, detail="Email is already registered")

    user = User(
        username=new_user.username,
        email=new_user.email,
        hashed_password=hash_password(new_user.password),
        role=Role.customer,  # never taken from the request
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    wrong_credentials = HTTPException(
        status_code=401,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = session.exec(select(User).where(User.username == form.username.lower())).first()
    if user is None:
        verify_password(form.password, DUMMY_HASH)  # same work as a real check
        raise wrong_credentials
    if not verify_password(form.password, user.hashed_password):
        raise wrong_credentials
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
```

### Registering

- **`role=Role.customer` is hardcoded.** Put that together with `UserCreateRequest` having no `role` field, and there is no request anyone can send that creates an admin.
- **409 Conflict** for a taken username or email. The database's `unique=True` is the backstop if this check is ever missed.
- **Only `hash_password(...)` is stored.** The real password exists in memory for the length of this one request and is never written anywhere.
- **`response_model=UserResponse`** means the hash never leaves the server.

> **An honest trade-off.** "Email is already registered" tells a stranger that this address has an account here. Most shops accept that, because a confusing sign-up page costs them customers. High-security services send an email instead of saying so on screen.

### Logging in

- **`OAuth2PasswordRequestForm = Depends()`** — login reads **form data**, not JSON. The OAuth2 standard says so, and it's what the `/docs` Authorize button sends. It's the reason `python-multipart` is installed. Send JSON here and you get a 422.
- **The same answer for an unknown user and a wrong password.** If they said "no such user" and "wrong password" separately, anyone could test which usernames exist here. Both get `401 Incorrect username or password`.
- **`DUMMY_HASH`** closes the same leak through *time*. Checking a password is slow on purpose (Part 6). If an unknown username came back instantly but a wrong password took tens of milliseconds longer, anyone timing the responses could tell the two apart — the delay would reveal what the message hides. Checking against a dummy hash makes both take the same time.
- **The disabled check comes after the password check**, so only someone who already knows the password finds out the account is disabled. A wrong password on a disabled account still gets the plain 401.

### Wire it up

**`main.py`**:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import create_db_and_tables
from app.routers import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(auth.router)


@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.app_name}"}
```

Only the `auth` router for now — each later part adds one line here. Run it:

```bash
uvicorn main:app --reload
```

If port 8000 is busy, Project 1's Part 5 covers `--port`.

### Try it

Open a second terminal (activate the venv there too) and sign up:

```bash
curl -X POST http://127.0.0.1:8000/auth/register -H "Content-Type: application/json" -d '{"username": "amina", "email": "amina@example.com", "password": "reads4ever"}'
```

```
{"id":1,"username":"amina","email":"amina@example.com","role":"customer","is_active":true}
```

No password, no hash. Now try to sign up as an admin:

```bash
curl -X POST http://127.0.0.1:8000/auth/register -H "Content-Type: application/json" -d '{"username": "sneaky", "email": "sneaky@example.com", "password": "letmein99", "role": "admin"}'
```

The response says `"role":"customer"`. The `"role": "admin"` was thrown away without a trace.

Log in — note there's no `Content-Type` this time, because `-d` on its own sends form data, which is exactly what login expects:

```bash
curl -X POST http://127.0.0.1:8000/auth/login -d "username=amina&password=reads4ever"
```

```
{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjox...","token_type":"bearer"}
```

Copy the whole `access_token` value and ask who you are:

```bash
curl http://127.0.0.1:8000/auth/me -H "Authorization: Bearer PASTE-YOUR-TOKEN-HERE"
```

Then ask without a token, with `-i` to see the headers:

```bash
curl -i http://127.0.0.1:8000/auth/me
```

```
HTTP/1.1 401 Unauthorized
www-authenticate: Bearer
{"detail":"Not authenticated"}
```

**Read your own token.** In the Python shell:

```python
import jwt
jwt.decode("PASTE-YOUR-TOKEN-HERE", options={"verify_signature": False})
```

```
{'sub': '1', 'exp': 1789073766}
```

No key needed to read it. Anyone who gets hold of a token can read this — and, far more importantly, can *use* the token until it expires. That's why Part 15 insists on HTTPS.

### The /docs login button

1. Open **http://127.0.0.1:8000/docs**. There's an **Authorize** button with a padlock.
2. Enter the username and password. Leave `client_id` and `client_secret` empty, click **Authorize**, then close the box.
3. The page now sends your token with every request. Open `GET /auth/me`, **Try it out**, **Execute** — and you get yourself back.

Routes that need a login show a padlock. That comes from `OAuth2PasswordBearer`, with no extra code.

**Checkpoint:** signing up with `"role": "admin"` still produces a customer, and `/auth/me` answers with a token and gives 401 without one.

---

## Part 10 — Roles: who is allowed to do what

**`app/dependencies.py`** — add this to the bottom:

```python
def require_roles(allowed_roles):
    """Build a dependency that only lets the given roles through."""

    def check_role(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403, detail="You do not have permission to do this"
            )
        return current_user

    return check_role
```

`require_roles` is **a function that builds and returns another function** — first-class functions from Week 1 · Lecture 2, §4.1, doing real work. `require_roles([Role.admin])` returns a `check_role` that remembers which roles are allowed. A route uses it like this:

```python
current_user: User = Depends(require_roles([Role.staff, Role.admin]))
```

- It depends on `get_current_user` first, so someone who isn't logged in gets **401** before any role is looked at. Only then does the role check run and give **403**.
- **The order of answers is always 401, then 403, then your route's own errors.** Dependencies run before the route body. So a customer who tries to delete a book that doesn't exist gets **403**, not 404 — someone who isn't allowed to delete books learns nothing about which books exist.
- **It's an allow-list.** You name the roles that *are* allowed. If someone adds a new role next year, it gets access to nothing until somebody decides otherwise.

### The first admin

There's a chicken-and-egg problem. Signing up always makes a customer, and only an admin can make someone an admin. So who makes the first one?

The answer is **someone who already has access to the server itself**, using a script. This is a standard pattern — Django's `createsuperuser` command does exactly the same thing.

**`create_admin.py`**:

```python
"""Create the first admin account.

    python create_admin.py

Nobody can register as an admin through the API -- that is the point -- so
the very first one has to be created from the command line, by someone who
already has access to the server.
"""

from getpass import getpass

from pydantic import ValidationError
from sqlmodel import Session, select

from app.database import create_db_and_tables, engine
from app.dtos.requests import UserCreateRequest
from app.enums import Role
from app.models import User
from app.security import hash_password


def create_admin(username, email, password):
    # Reuse UserCreateRequest so an admin obeys exactly the same rules as everyone else.
    details = UserCreateRequest(username=username, email=email, password=password)

    with Session(engine) as session:
        taken = session.exec(
            select(User).where(
                (User.username == details.username) | (User.email == details.email)
            )
        ).first()
        if taken:
            raise ValueError("A user with that username or email already exists")

        admin = User(
            username=details.username,
            email=details.email,
            hashed_password=hash_password(details.password),
            role=Role.admin,
        )
        session.add(admin)
        session.commit()
        session.refresh(admin)
        return admin


if __name__ == "__main__":
    create_db_and_tables()

    username = input("Admin username: ")
    email = input("Admin email: ")
    password = getpass("Admin password (nothing will show as you type): ")

    try:
        admin = create_admin(username, email, password)
    except ValidationError as error:  # must come BEFORE ValueError
        print("Could not create admin:")
        for problem in error.errors():
            print(f"  {problem['loc'][0]}: {problem['msg']}")
    except ValueError as error:
        print(f"Could not create admin: {error}")
    else:
        print(f"Created admin '{admin.username}' with id {admin.id}")
```

- **`if __name__ == "__main__":`** means that block runs only when you run this file directly, and not if something imports it.
- **It reuses `UserCreateRequest`**, so an admin has to obey the same username, email and password rules as everybody else.
- **`getpass`** hides the password as you type it.
- **The order of the `except` blocks matters.** `ValidationError` is a *subclass* of `ValueError` — inheritance from Week 1 · Lecture 2. Python checks `except` blocks from top to bottom, so if `ValueError` came first it would catch validation errors too, and the friendly per-field messages would never print.

Run it (the server can keep running in the other terminal):

```bash
python create_admin.py
```

```
Admin username: owner
Admin email: owner@example.com
Admin password (nothing will show as you type):
Created admin 'owner' with id 3
```

It's id 3 because `amina` and `sneaky` already exist from Part 9. Run it once more with a password that's too short, and it tells you why:

```
Could not create admin:
  password: String should have at least 8 characters
```

**Checkpoint:** in `/docs`, click **Authorize**, **Logout**, and log in as `owner`. `GET /auth/me` now shows `"role": "admin"`.

---

## Part 11 — Managing users

**`app/routers/users.py`**:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import require_roles
from app.dtos.requests import ActiveUpdateRequest, RoleUpdateRequest
from app.dtos.responses import UserResponse
from app.enums import Role
from app.models import User

router = APIRouter(prefix="/users", tags=["users"])

admin_only = require_roles([Role.admin])


def get_user_or_404(session, user_id):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("", response_model=list[UserResponse])
def list_users(
    role: Role | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(admin_only),
):
    query = select(User)
    if role is not None:
        query = query.where(User.role == role)
    return session.exec(query).all()


@router.patch("/{user_id}/role", response_model=UserResponse)
def change_role(
    user_id: int,
    update: RoleUpdateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(admin_only),
):
    user = get_user_or_404(session, user_id)
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot change your own role")
    user.role = update.role
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.patch("/{user_id}/active", response_model=UserResponse)
def set_active(
    user_id: int,
    update: ActiveUpdateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(admin_only),
):
    user = get_user_or_404(session, user_id)
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot disable your own account")
    user.is_active = update.is_active
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
```

In **`main.py`**, change the import line to:

```python
from app.routers import auth, users
```

and add this under the existing `include_router` line:

```python
app.include_router(users.router)
```

- **`admin_only` is built once** at the top of the file and reused by every route, instead of calling `require_roles` three times.
- **`?role=`** is an Enum used as a query parameter — Lecture 2, §3.2 — so `GET /users?role=staff` works and `?role=superuser` is a 422.
- **You can't change your own role or disable your own account** — both are a 400. The easiest way to lock everyone out of admin is for the only admin to demote themselves by mistake.
- **Disable, don't delete.** A disabled user's orders still point at a real account.

> **Worth knowing.** `APIRouter(prefix="/users", dependencies=[Depends(admin_only)])` would protect every route in the router in one line. It's a good pattern. It isn't used here only because `change_role` and `set_active` need `current_user` in hand, to compare ids.

### Try it in /docs, logged in as `owner`

1. `GET /users` — everyone is listed, and nobody's password hash is in the output.
2. `GET /users` with `role` set to `staff` — an empty list for now.
3. `PATCH /users/{user_id}/role` for `amina` with `{"role": "staff"}` — 200, and she's staff.
4. The same route with **your own** id — **400**, `You cannot change your own role`.
5. `PATCH /users/{user_id}/active` for `sneaky` with `{"is_active": false}` — 200.

Then **Logout** and log in as `amina`: `GET /users` gives **403**.

**Checkpoint:** an admin can promote someone, can't demote themselves, and a non-admin gets 403 from every `/users` route.

---

## Part 12 — The books

**`app/dtos/requests.py`** — add to the bottom:

```python
# ----------------------------------------------------------------- books

class BookCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    genre: Genre = Genre.fiction
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)

    @field_validator("title", "author")
    @classmethod
    def not_blank(cls, value):
        if not value.strip():
            raise ValueError("cannot be blank")
        return value.strip()


class BookUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, min_length=1, max_length=100)
    genre: Genre | None = None
    price: float | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)

    @field_validator("title", "author")
    @classmethod
    def not_blank(cls, value):
        if value is None:
            return value
        if not value.strip():
            raise ValueError("cannot be blank")
        return value.strip()
```

**`app/dtos/responses.py`** — add to the bottom:

```python
# ----------------------------------------------------------------- books

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: Genre
    price: float
    stock: int
```

- **`Genre`** is used on `BookCreateRequest` and, in the router below, as a `?genre=` query parameter — Lecture 2, §3.2.
- **One validator on two fields:** `@field_validator("title", "author")`. This is Lecture 2 §3.3's whitespace case — `Field(min_length=1)` lets `"   "` through, the validator doesn't.
- **`BookUpdateRequest`** makes every field optional so staff can PATCH just the price. Its validator has to let `None` pass, or leaving a field out would crash it.

> **An honest simplification.** `price` is a `float`, and floats can't store money exactly — in Python, `0.1 + 0.2` is `0.30000000000000004`. Real shops store money as `Decimal` or as whole cents. A float keeps this guide simple; just don't build a real shop on it.

**`app/routers/books.py`**:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import require_roles
from app.dtos.requests import BookCreateRequest, BookUpdateRequest
from app.dtos.responses import BookResponse
from app.enums import Genre, Role
from app.models import Book, Order, User

router = APIRouter(prefix="/books", tags=["books"])

staff_or_admin = require_roles([Role.staff, Role.admin])
admin_only = require_roles([Role.admin])


def get_book_or_404(session, book_id):
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


# ---- anyone, no login needed ------------------------------------------

@router.get("", response_model=list[BookResponse])
def list_books(
    genre: Genre | None = None,
    in_stock: bool = False,
    session: Session = Depends(get_session),
):
    query = select(Book)
    if genre is not None:
        query = query.where(Book.genre == genre)
    if in_stock:
        query = query.where(Book.stock > 0)
    return session.exec(query).all()


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, session: Session = Depends(get_session)):
    return get_book_or_404(session, book_id)


# ---- staff and admins -------------------------------------------------

@router.post("", response_model=BookResponse, status_code=201)
def create_book(
    new_book: BookCreateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(staff_or_admin),
):
    book = Book.model_validate(new_book.model_dump())  # book.id is None here
    session.add(book)
    session.commit()  # the database assigns the next id
    session.refresh(book)  # reload the saved row, new id included
    return book


@router.patch("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    update: BookUpdateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(staff_or_admin),
):
    book = get_book_or_404(session, book_id)
    changes = update.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in changes.items():
        setattr(book, field, value)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


# ---- admins only ------------------------------------------------------

@router.delete("/{book_id}", status_code=204)
def delete_book(
    book_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(admin_only),
):
    book = get_book_or_404(session, book_id)
    if session.exec(select(Order).where(Order.book_id == book_id)).first():
        raise HTTPException(
            status_code=409,
            detail="This book has orders. Set its stock to 0 instead of deleting it.",
        )
    session.delete(book)
    session.commit()
```

In **`main.py`**, make the import `from app.routers import auth, books, users` and add `app.include_router(books.router)`.

- **The two read routes have no user dependency at all.** That alone makes them public: no login needed, and no padlock in `/docs`.
- **The write routes ask for `current_user`** and never use it. Asking for it is what enforces the check.
- **`""` instead of `"/"`.** The lecture writes `@router.get("/")`, which makes the address `/books/` with a slash on the end. An empty string makes it exactly `/books`, which is what the commands in Part 14 use. `/books/` still works — FastAPI redirects it — but `curl` doesn't follow redirects unless you add `-L`.
- **`exclude_unset=True, exclude_none=True`** — only the fields the client actually sent, *and* not ones sent as `null`. Without `exclude_none`, a request of `{"title": null}` would try to store nothing in a column that has to have a title, and crash with a 500.
- **`Book.model_validate(new_book.model_dump())`** turns the request DTO into a dict, and the dict into an entity — a `Book` whose `id` is still `None`. The `commit` is where the database gives it one, exactly as Part 5 describes; the comments in `create_book` mark each step.
- **Deleting a book that has orders is a 409.** Removing it would leave orders pointing at nothing. The message tells staff what to do instead: set the stock to 0.

### Try it in /docs

1. As `amina` (who's staff now), `POST /books` with `{"title": "Dune", "author": "Frank Herbert", "genre": "fiction", "price": 12.5, "stock": 3}` — **201**.
2. `DELETE /books/{book_id}` as `amina` — **403**. Staff can add books; only admins can remove them.
3. **Logout** completely. `GET /books` still works, `?genre=poetry` filters, and `?genre=mystery` is a 422.

**Checkpoint:** reading books needs no login, adding them needs staff, and deleting them needs admin.

---

## Part 13 — Orders, and authorization by ownership

Role checks answer *"is this kind of user allowed?"* Orders need a second, different question: *"is this **their** order?"* A customer is allowed to see orders — just not anybody else's. That's **ownership**, and a role check alone can't express it.

**`app/dtos/requests.py`** — add to the bottom:

```python
# ---------------------------------------------------------------- orders

class OrderCreateRequest(BaseModel):
    book_id: int  # refers to a book that already exists
    quantity: int = Field(default=1, ge=1, le=10)


class OrderStatusUpdateRequest(BaseModel):
    status: OrderStatus
```

**`app/dtos/responses.py`** — add to the bottom:

```python
# ---------------------------------------------------------------- orders

class OrderResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    quantity: int
    total_price: float
    status: OrderStatus
    created_at: datetime
```

Look at what **`OrderCreateRequest`** doesn't have: an `id`, a `user_id`, or a price. The client names the book and how many copies — and `book_id` only *refers to* a book that already exists; it doesn't choose a new id. Everything else is decided by the server.

**`app/routers/orders.py`**:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies import get_current_user, require_roles
from app.dtos.requests import OrderCreateRequest, OrderStatusUpdateRequest
from app.dtos.responses import OrderResponse
from app.enums import OrderStatus, Role
from app.models import Book, Order, User

router = APIRouter(prefix="/orders", tags=["orders"])

STAFF_ROLES = [Role.staff, Role.admin]
staff_or_admin = require_roles(STAFF_ROLES)


@router.post("", response_model=OrderResponse, status_code=201)
def place_order(
    new_order: OrderCreateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    book = session.get(Book, new_order.book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.stock < new_order.quantity:
        raise HTTPException(status_code=409, detail=f"Only {book.stock} left in stock")

    book.stock -= new_order.quantity
    order = Order(
        user_id=current_user.id,  # from the token -- never from the request
        book_id=book.id,
        quantity=new_order.quantity,
        total_price=round(book.price * new_order.quantity, 2),
    )
    session.add(book)
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.get("", response_model=list[OrderResponse])
def list_orders(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    query = select(Order)
    if current_user.role not in STAFF_ROLES:
        query = query.where(Order.user_id == current_user.id)
    return session.exec(query).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id and current_user.role not in STAFF_ROLES:
        # 404, not 403: don't confirm to a stranger that this order exists.
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    update: OrderStatusUpdateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(staff_or_admin),
):
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status == OrderStatus.cancelled:
        raise HTTPException(status_code=400, detail="A cancelled order cannot be changed")

    if update.status == OrderStatus.cancelled:
        book = session.get(Book, order.book_id)
        if book is not None:
            book.stock += order.quantity  # put the books back on the shelf
            session.add(book)

    order.status = update.status
    session.add(order)
    session.commit()
    session.refresh(order)
    return order
```

And the final **`main.py`**, with every router plugged in:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import create_db_and_tables
from app.routers import auth, books, orders, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(books.router)
app.include_router(orders.router)


@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.app_name}"}
```

- **`user_id=current_user.id` comes from the token.** A request that sends `"user_id": 1` has it thrown away, just like `role` at sign-up. If the body could choose, anyone could place orders on someone else's account.
- **`total_price` is calculated on the server.** If the client sent it, anyone could decide their own price.
- **409 Conflict** when there isn't enough stock: the request is perfectly valid, it just clashes with the current state of the shop.
- **`list_orders`** is one URL that gives different results depending on who's asking: customers see only their own orders, staff see all of them.
- **`get_order` answers 404, not 403, for someone else's order.** A 403 would confirm *"order 7 exists, it just isn't yours"* — and because ids go up one at a time, a stranger could count every order the shop has ever had. A 404 gives nothing away.
- **Cancelling puts the books back on the shelf, and a cancelled order can't be reopened** (400). Without that rule, cancel → reopen → cancel again would put the same books back twice.

> **An honest gap.** If two customers order the last copy at the same instant, both requests could pass the stock check before either one saves. Real shops lock the row, or subtract in a single `UPDATE ... WHERE stock >= quantity`. That's beyond this guide, and on a single development server you won't hit it.

**Checkpoint:** in `/docs`, re-enable `sneaky` as `owner`, then log in as `sneaky` and order a book. Next, register a brand-new customer with `POST /auth/register` (no login needed), log in as them, and `GET /orders/{order_id}` for sneaky's order: **404**. Log in as `amina`, who is staff, and the same request gives **200**.

---

## Part 14 — Walk through it as three people

This runs the whole permission table from Part 0 in about a minute, from a clean start.

1. Stop the server with `Ctrl+C`.
2. Delete `bookstore.db`.
3. `python create_admin.py` — username `owner`, email `owner@example.com`, password `Admin12345`.
4. Start the server again: `uvicorn main:app --reload`.

In a second terminal with the venv active, run the blocks below in order. They're for macOS and Linux (on Windows, use Git Bash or WSL — or do the same steps in `/docs`). The ids assume this fresh database: `owner` is 1, `amina` 2, `karim` 3.

**Set up some shortcuts.** `SHOW` makes every command print its status code at the end; `login` logs someone in and keeps only the token:

```bash
BASE=http://127.0.0.1:8000
JSON="Content-Type: application/json"
SHOW="  -> %{http_code}\n"

login() {
  curl -s -X POST "$BASE/auth/login" -d "username=$1&password=$2" \
    | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])"
}
```

**1. Two customers sign up** — `201`, `201`:

```bash
curl -s -w "$SHOW" -X POST "$BASE/auth/register" -H "$JSON" -d '{"username": "amina", "email": "amina@example.com", "password": "reads4ever"}'
curl -s -w "$SHOW" -X POST "$BASE/auth/register" -H "$JSON" -d '{"username": "karim", "email": "karim@example.com", "password": "shelves22"}'
```

**2. Everyone logs in** — no output, the tokens go into variables:

```bash
OWNER=$(login owner Admin12345)
AMINA=$(login amina reads4ever)
KARIM=$(login karim shelves22)
```

**3. Karim, a customer, tries to stock the shelves** — `403`:

```bash
curl -s -w "$SHOW" -X POST "$BASE/books" -H "$JSON" -H "Authorization: Bearer $KARIM" -d '{"title": "Dune", "author": "Frank Herbert", "genre": "fiction", "price": 12.5, "stock": 3}'
```

**4. The admin makes Karim staff** — `200`:

```bash
curl -s -w "$SHOW" -X PATCH "$BASE/users/3/role" -H "$JSON" -H "Authorization: Bearer $OWNER" -d '{"role": "staff"}'
```

**5. Karim tries again with the same token, without logging in again** — `201`, `201`, `201`. The second request also sends `"id": 99`; look at its response — the database gave the book id `2` anyway:

```bash
curl -s -w "$SHOW" -X POST "$BASE/books" -H "$JSON" -H "Authorization: Bearer $KARIM" -d '{"title": "Dune", "author": "Frank Herbert", "genre": "fiction", "price": 12.5, "stock": 3}'
curl -s -w "$SHOW" -X POST "$BASE/books" -H "$JSON" -H "Authorization: Bearer $KARIM" -d '{"id": 99, "title": "Sapiens", "author": "Yuval Noah Harari", "genre": "nonfiction", "price": 18.0, "stock": 5}'
curl -s -w "$SHOW" -X POST "$BASE/books" -H "$JSON" -H "Authorization: Bearer $KARIM" -d '{"title": "Leaves of Grass", "author": "Walt Whitman", "genre": "poetry", "price": 9.0, "stock": 0}'
```

**6. A visitor who isn't logged in browses what's in stock** — `200`, two books:

```bash
curl -s -w "$SHOW" "$BASE/books?in_stock=true"
```

**7. Amina buys two copies of Dune, then tries for two more** — `201`, then `409` with `Only 1 left in stock`:

```bash
curl -s -w "$SHOW" -X POST "$BASE/orders" -H "$JSON" -H "Authorization: Bearer $AMINA" -d '{"book_id": 1, "quantity": 2}'
curl -s -w "$SHOW" -X POST "$BASE/orders" -H "$JSON" -H "Authorization: Bearer $AMINA" -d '{"book_id": 1, "quantity": 2}'
```

**8. Karim orders, and tries to put it on Amina's account** — `201`, but the response says `"user_id":3`:

```bash
curl -s -w "$SHOW" -X POST "$BASE/orders" -H "$JSON" -H "Authorization: Bearer $KARIM" -d '{"book_id": 2, "quantity": 1, "user_id": 2}'
```

**9. Ownership** — Amina sees only her own order, gets `404` for Karim's, and Karim, as staff, sees both:

```bash
curl -s -w "$SHOW" "$BASE/orders" -H "Authorization: Bearer $AMINA"
curl -s -w "$SHOW" "$BASE/orders/2" -H "Authorization: Bearer $AMINA"
curl -s -w "$SHOW" "$BASE/orders" -H "Authorization: Bearer $KARIM"
```

**10. Deleting** — staff `403`; the admin gets `409` for a book with orders, and `204` for one without:

```bash
curl -s -w "$SHOW" -X DELETE "$BASE/books/3" -H "Authorization: Bearer $KARIM"
curl -s -w "$SHOW" -X DELETE "$BASE/books/1" -H "Authorization: Bearer $OWNER"
curl -s -w "$SHOW" -X DELETE "$BASE/books/3" -H "Authorization: Bearer $OWNER"
```

**11. Ids are never reused.** Book 3 was just deleted. The admin adds a new book, and it gets id `4` — not `3` — `201`:

```bash
curl -s -w "$SHOW" -X POST "$BASE/books" -H "$JSON" -H "Authorization: Bearer $OWNER" -d '{"title": "Persuasion", "author": "Jane Austen", "price": 8.0, "stock": 4}'
```

**12. Taking access away works instantly.** The admin demotes Karim (`200`), and the *same token* that added books in step 5 now gets `403`. Then the admin disables Amina (`200`), and her token gets `403 Account is disabled`:

```bash
curl -s -w "$SHOW" -X PATCH "$BASE/users/3/role" -H "$JSON" -H "Authorization: Bearer $OWNER" -d '{"role": "customer"}'
curl -s -w "$SHOW" -X POST "$BASE/books" -H "$JSON" -H "Authorization: Bearer $KARIM" -d '{"title": "Emma", "author": "Jane Austen", "price": 7.5, "stock": 2}'
curl -s -w "$SHOW" -X PATCH "$BASE/users/2/active" -H "$JSON" -H "Authorization: Bearer $OWNER" -d '{"is_active": false}'
curl -s -w "$SHOW" "$BASE/auth/me" -H "Authorization: Bearer $AMINA"
```

Step 12 is the one worth pausing on. Neither Karim nor Amina logged out, and both tokens are still perfectly valid JWTs that haven't expired. They stopped working because every request checks the database, exactly as Part 8 promised.

**Checkpoint:** every status code matches the one written above its block.

---

## Part 15 — What this guide deliberately leaves out

This is a solid foundation, not a finished production system. Here is what's missing, so you know what to look for next:

- **HTTPS.** A bearer token works for whoever holds it, until it expires. Over plain HTTP, anyone on the same network can copy tokens as they pass. `127.0.0.1` on your own machine is fine; anything real must use HTTPS.
- **Logging out.** You can't un-issue a JWT. A short expiry limits the damage, and disabling an account works instantly here because of Part 8's database check. Real apps add *refresh tokens* or keep a list of revoked tokens.
- **Brute-force protection.** Nothing stops someone trying ten thousand passwords against `amina`. Real apps rate-limit login attempts and lock accounts for a while after repeated failures.
- **Password reset and email verification.** Both need to send email.
- **Checks and balances on admins.** Two admins can still demote each other, and nothing records who changed what. Real apps keep an audit log.
- **Browsers.** A website on a different address calling this API needs `CORSMiddleware`, and where a browser keeps the token is a security decision in its own right.
- **Simultaneous orders** (Part 13) and **money as a float** (Part 12).

---

## Part 16 — Where everything came from

From the course so far:

| What you used | Where it came from |
|---|---|
| `Role`, `Genre`, `OrderStatus` as `(str, Enum)` | Week 2 · Lecture 2, §2.4 |
| An Enum as a query parameter: `?role=`, `?genre=` | Week 2 · Lecture 2, §3.2 |
| `@field_validator` for usernames, passwords and titles | Week 2 · Lecture 2, §3.3 |
| `BaseSettings` and `.env` | Week 2 · Lecture 2, §3.4 |
| Request and response DTOs, kept apart from routes and tables | Week 2 · Lecture 2, §4.1 — where they're called *schemas* |
| `APIRouter` with `prefix` and `tags`, in a `routers/` package | Week 2 · Lecture 2, §4.2–4.3 |
| `response_model` keeping the password hash private | Week 2 · Lecture 1, §4.4 — and Project 1, Part 12 |
| The database assigning ids on `commit` | Project 1, Parts 7–8 |
| 401 vs. 403, the same shape as 422 vs. 404 | Week 2 · Lecture 1, §4.3 — and Project 1, Part 13 |
| `require_roles` returning a function | Week 1 · Lecture 2, §4.1 |
| `ValidationError` being a kind of `ValueError` | Week 1 · Lecture 2, §3.1 |

Still ahead:

| What you used | When it gets explained |
|---|---|
| SQLModel tables, foreign keys and sessions | Week 3 |
| Automated tests proving a customer really gets 403 | Week 3 |
| `async` and `@asynccontextmanager` | Week 4 |
| Linting and formatting this code | Week 4 |

**If you want to push further:** give every book a nested `Author` model with its own validator (Lecture 2, §3.1); add `POST /auth/change-password`, which must check the *current* password first; let a customer cancel their own order while it's still pending — that's ownership and a status rule at once; or add a `?status=` filter to `GET /orders` using `OrderStatus`.

---

## Troubleshooting

**`zsh: no matches found: pwdlib[argon2]`**
The square brackets need quotes: `pip install "pwdlib[argon2]"`. See Part 1.

**`ValidationError: 1 validation error for Settings` — `secret_key` `Field required`**
The app can't find your key. Either `.env` doesn't exist, it isn't in the folder you're running from, or `config.py` is missing the `model_config = SettingsConfigDict(env_file=".env")` line. See Part 3.

**`String should have at least 32 characters`**
Your `SECRET_KEY` is too short. Generate a proper one with the command in Part 3.

**`RuntimeError: Form data requires "python-multipart" to be installed.`**
The server won't start at all — this appears in the `uvicorn` output as soon as it loads `main.py`, because the login route reads form data. Run `pip install python-multipart`.

**`ModuleNotFoundError: No module named 'jwt'`**
Install `pyjwt`. The import name is `jwt`, but the package name is not.

**`AttributeError: module 'jwt' has no attribute 'encode'`**
You installed the wrong package, the one named plain `jwt`. Run `pip uninstall jwt`, then `pip install pyjwt`.

**`401 Not authenticated` from a route in `/docs`**
You haven't clicked **Authorize** yet, or you're on a page you reloaded — log in again with the padlock button.

**Everything suddenly returns 401 after about half an hour**
Your token expired. Log in again. The lifetime is `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`.

**Everyone got logged out after I changed `SECRET_KEY`**
That's expected — every existing token was signed with the old key. Passwords still work; just log in again.

**`403 You do not have permission to do this`**
You're logged in, but your role isn't allowed to do that. Check who you are with `GET /auth/me`, and compare with the table in Part 0.

**`403 Account is disabled`**
An admin disabled this account. Re-enable it with `PATCH /users/{user_id}/active` as an admin.

**Login returns 422**
You sent JSON. Login takes form data: `-d "username=...&password=..."` with no `Content-Type` header.

**`307 Temporary Redirect`**
You put a slash on the end — `/books/` instead of `/books`. Remove it, or add `-L` to `curl`.

**`sqlite3.OperationalError: no such column` after editing `models.py`**
`create_all` creates missing tables, but it never changes a table that already exists. Delete `bookstore.db`, restart, and run `python create_admin.py` again.

**`ModuleNotFoundError: No module named 'app.schemas'`**
An earlier version of this guide kept every DTO in `app/schemas.py`. They now live in `app/dtos/requests.py` and `app/dtos/responses.py`, with the enums in `app/enums.py`. Update the import lines to match Parts 4 and 9–13.

**A deleted book's id got used again**
Your `bookstore.db` was created before `sqlite_autoincrement=True` was added. `create_all` never changes a table that already exists, so delete `bookstore.db`, restart, and run `python create_admin.py` again.

**`ModuleNotFoundError: No module named 'app'`**
Run `uvicorn` and `python create_admin.py` from the `project-2` folder itself, not from inside `app/`.
