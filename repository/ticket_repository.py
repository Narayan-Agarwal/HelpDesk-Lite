"""
Data-access layer. All SQL lives here so routes and models
never talk to the database directly — this is the seam that
would let you swap SQLite for PostgreSQL later without
touching business logic.
"""

import sqlite3
from models import Ticket, Agent, Employee

DB_PATH = "helpdesk.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('employee', 'agent'))
        );

        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            assigned_agent_id INTEGER,
            created_at TEXT NOT NULL,
            FOREIGN KEY (assigned_agent_id) REFERENCES users(user_id)
        );
        """
    )
    # Seed a couple of agents/employees if empty, so the app is usable immediately
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO users (name, role) VALUES (?, ?)",
            [("Ritika (Employee)", "employee"),
             ("Sourav (Employee)", "employee"),
             ("Priya (Agent)", "agent"),
             ("Anil (Agent)", "agent")],
        )
    conn.commit()
    conn.close()


def get_all_users():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    users = []
    for r in rows:
        cls = Agent if r["role"] == "agent" else Employee
        users.append(cls(r["user_id"], r["name"]))
    return users


def get_agents():
    return [u for u in get_all_users() if isinstance(u, Agent)]


def get_user(user_id):
    for u in get_all_users():
        if u.user_id == int(user_id):
            return u
    return None


def _row_to_ticket(row):
    return Ticket(
        ticket_id=row["ticket_id"],
        title=row["title"],
        description=row["description"],
        priority=row["priority"],
        status=row["status"],
        assigned_agent_id=row["assigned_agent_id"],
        created_at=row["created_at"],
    )


def get_all_tickets():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tickets ORDER BY ticket_id DESC").fetchall()
    conn.close()
    return [_row_to_ticket(r) for r in rows]


def get_ticket(ticket_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)
    ).fetchone()
    conn.close()
    return _row_to_ticket(row) if row else None


def create_ticket(title, description, priority):
    ticket = Ticket(ticket_id=None, title=title, description=description, priority=priority)
    conn = get_connection()
    conn.execute(
        "INSERT INTO tickets (title, description, priority, status, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (ticket.title, ticket.description, ticket.priority, ticket.status, ticket.created_at),
    )
    conn.commit()
    conn.close()


def save_ticket(ticket: Ticket):
    """Persist a Ticket object's current state back to the DB."""
    conn = get_connection()
    conn.execute(
        "UPDATE tickets SET status = ?, assigned_agent_id = ? WHERE ticket_id = ?",
        (ticket.status, ticket.assigned_agent_id, ticket.ticket_id),
    )
    conn.commit()
    conn.close()
