# HelpDesk Lite

A small internal ticketing console — employees raise tickets, agents assign,
resolve, or escalate them. Built to practice object-oriented design and a
proper Flask/DB architecture rather than a single-file script.

**Live demo:** _add your Render URL here_
**Stack:** Flask, SQLite, vanilla HTML/CSS (no JS framework)

## Why this exists

Most of my other projects (see [MetaMind](https://github.com/Narayan-Agarwal/metamind),
[SkillScope](https://github.com/Narayan-Agarwal/skillscope)) are data/analytics
apps built on Streamlit. This one is deliberately different: a plain CRUD +
workflow app in the shape of enterprise software, to practice OOP design and
a Flask backend with a real templated frontend.

## Architecture

```
models.py                  → domain layer (OOP)
  User (base)
    ├── Employee            raises tickets
    └── Agent                assigns/resolves/escalates tickets
  Ticket                     owns its own status transitions
                              (assign(), resolve(), escalate())

repository/
  ticket_repository.py      → data-access layer, all SQL lives here
                               (routes/models never touch SQL directly)

app.py                      → Flask routes (thin — delegate to models/repo)
templates/                  → Jinja2 templates
static/style.css            → styling
```

The split matters more than the size of the app: business rules (a ticket
can't be resolved before it's assigned) live in `Ticket.resolve()`, not
scattered across routes or templates. Swapping SQLite for PostgreSQL later
would only touch `repository/ticket_repository.py`.

## Running locally

```bash
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5000`. The role switcher in the top bar toggles
between an Employee view (raise tickets) and an Agent view (assign / resolve
/ escalate) — no login system, kept intentionally out of scope.

## Deploying (Render)

1. Push this repo to GitHub.
2. On Render: New → Web Service → connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`

## What I'd add with more time

- Real authentication instead of the role-switch dropdown
- A `Comment` model for ticket discussion threads
- Pagination on the dashboard table
