from flask import Flask, render_template, request, redirect, url_for, session

from repository import ticket_repository as repo
from models import Ticket

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"

with app.app_context():
    repo.init_db()


@app.route("/")
def dashboard():
    tickets = repo.get_all_tickets()
    current_role = session.get("role", "employee")
    return render_template(
        "dashboard.html",
        tickets=tickets,
        current_role=current_role,
        status_counts=_status_counts(tickets),
    )


@app.route("/switch-role", methods=["POST"])
def switch_role():
    session["role"] = request.form.get("role", "employee")
    return redirect(url_for("dashboard"))


@app.route("/tickets/new", methods=["GET", "POST"])
def new_ticket():
    if request.method == "POST":
        repo.create_ticket(
            title=request.form["title"],
            description=request.form.get("description", ""),
            priority=request.form["priority"],
        )
        return redirect(url_for("dashboard"))
    return render_template("new_ticket.html")


@app.route("/tickets/<int:ticket_id>")
def ticket_detail(ticket_id):
    ticket = repo.get_ticket(ticket_id)
    agents = repo.get_agents()
    assigned_agent = repo.get_user(ticket.assigned_agent_id) if ticket.assigned_agent_id else None
    current_role = session.get("role", "employee")
    return render_template(
        "ticket_detail.html",
        ticket=ticket,
        agents=agents,
        assigned_agent=assigned_agent,
        current_role=current_role,
    )


@app.route("/tickets/<int:ticket_id>/assign", methods=["POST"])
def assign_ticket(ticket_id):
    ticket = repo.get_ticket(ticket_id)
    agent = repo.get_user(request.form["agent_id"])
    ticket.assign(agent)  # OOP method owns the transition + validation
    repo.save_ticket(ticket)
    return redirect(url_for("ticket_detail", ticket_id=ticket_id))


@app.route("/tickets/<int:ticket_id>/resolve", methods=["POST"])
def resolve_ticket(ticket_id):
    ticket = repo.get_ticket(ticket_id)
    try:
        ticket.resolve()
        repo.save_ticket(ticket)
    except ValueError:
        pass  # e.g. resolving an unassigned ticket — silently ignored for this scope
    return redirect(url_for("ticket_detail", ticket_id=ticket_id))


@app.route("/tickets/<int:ticket_id>/escalate", methods=["POST"])
def escalate_ticket(ticket_id):
    ticket = repo.get_ticket(ticket_id)
    ticket.escalate()
    repo.save_ticket(ticket)
    return redirect(url_for("ticket_detail", ticket_id=ticket_id))


def _status_counts(tickets):
    counts = {"Open": 0, "In Progress": 0, "Resolved": 0, "Escalated": 0}
    for t in tickets:
        counts[t.status] = counts.get(t.status, 0) + 1
    return counts


if __name__ == "__main__":
    app.run(debug=True)
