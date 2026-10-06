# HelpDesk Lite

A small internal ticketing console — employees raise tickets, agents assign, resolve or escalate them. Built to practice object-oriented design and a proper Flask/DB architecture rather than a single-file script.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-storage-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

> This is a **deliberately small CRUD + workflow app** in the shape of enterprise software — a
> layering and OOP exercise, not a pipeline or analytics product. There is no login system; a
> role switcher stands in for authentication, kept out of scope on purpose.

## The problem

Most of my other projects are data/analytics apps built on Streamlit. This one is deliberately
different: a plain create-read-update-workflow app where the interesting part is not the feature
set but the boundaries — business rules live in domain objects, SQL lives behind a repository,
and Flask routes stay thin.

## Architecture

```
models.py                  → domain layer (OOP)
  User (base)
    ├── Employee            raises tickets
    └── Agent                assigns / resolves / escalates tickets
  Ticket                     owns its own status transitions
                              assign() → In Progress
                              resolve() → raises if status is Open
                              escalate() → Escalated

repository/
  ticket_repository.py      → data-access layer; all SQL (sqlite3) lives here
                               routes and models never touch SQL directly

app.py                      → Flask routes (thin — delegate to models/repo)
templates/                  → Jinja2 templates (base, dashboard, new ticket, detail)
static/style.css            → styling
```

**Routes** (`app.py`): dashboard `/`, role switch `/switch-role`, create `/tickets/new`,
detail `/tickets/<id>`, and the workflow actions `/assign`, `/resolve`, `/escalate` (all POST).
The dashboard shows status counts computed from the ticket list.

The split matters more than the size of the app: business rules (a ticket can't be resolved
before it's assigned) live in `Ticket.resolve()`, not scattered across routes or templates.
Swapping SQLite for PostgreSQL later would only touch `repository/ticket_repository.py`.

## How to run locally

```cmd
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python app.py
```

Visit `http://localhost:5000`. The role switcher in the top bar toggles between an Employee view
(raise tickets) and an Agent view (assign / resolve / escalate). The SQLite database
(`helpdesk.db`) is created on first start.

## Tests

There is no automated test suite yet.

## Data sources

No external data and no APIs — all state lives in a local SQLite file created by the app.

## Limitations

- No authentication or authorization: the Employee/Agent switch is a session toggle, not a login.
- The Flask `secret_key` is a hardcoded development value in `app.py`; any real deployment should
  read it from the environment.
- No tests, no CI.
- SQLite is fine for a demo but is not designed for concurrent multi-user writes.

## Deploying (Render)

1. Push this repo to GitHub.
2. On Render: New → Web Service → connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app` (already defined in [`Procfile`](Procfile)).

No live URL is linked here — the app has not been deployed yet.

## Project structure

```
HelpDesk-Lite/
├── app.py                     # Flask routes
├── models.py                  # User / Employee / Agent / Ticket domain objects
├── repository/
│   └── ticket_repository.py   # All SQL (sqlite3), init_db(), CRUD
├── templates/                 # base, dashboard, new_ticket, ticket_detail
├── static/style.css
├── Procfile                   # web: gunicorn app:app
└── requirements.txt           # Flask 3.0.3, gunicorn 22.0.0
```

## Licence

MIT — see [LICENSE](LICENSE).
