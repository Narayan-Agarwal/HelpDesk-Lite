"""
Domain models for HelpDesk Lite.

This module is the OOP core of the app: a small User hierarchy
(Employee / Agent) and a Ticket class that owns its own state
transitions instead of leaving that logic scattered in routes.
"""

from datetime import datetime


class User:
    """Base class for anyone using the system."""

    def __init__(self, user_id: int, name: str):
        self.user_id = user_id
        self.name = name

    def role(self) -> str:
        return "user"

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"


class Employee(User):
    """Raises tickets. Cannot resolve or assign them."""

    def role(self) -> str:
        return "employee"


class Agent(User):
    """Can be assigned tickets and resolve/escalate them."""

    def role(self) -> str:
        return "agent"


class Ticket:
    """
    A support ticket. Encapsulates its own status and the rules
    for how that status is allowed to change, rather than letting
    routes/templates mutate status directly.
    """

    VALID_STATUSES = ("Open", "In Progress", "Resolved", "Escalated")
    VALID_PRIORITIES = ("Low", "Medium", "High")

    def __init__(self, ticket_id, title, description, priority,
                 status="Open", assigned_agent_id=None, created_at=None):
        if priority not in self.VALID_PRIORITIES:
            raise ValueError(f"Invalid priority: {priority}")

        self.ticket_id = ticket_id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.assigned_agent_id = assigned_agent_id
        self.created_at = created_at or datetime.utcnow().isoformat(timespec="seconds")

    def assign(self, agent: Agent):
        if not isinstance(agent, Agent):
            raise TypeError("Tickets can only be assigned to an Agent")
        self.assigned_agent_id = agent.user_id
        self.status = "In Progress"

    def resolve(self):
        if self.status == "Open":
            raise ValueError("Cannot resolve a ticket that hasn't been assigned yet")
        self.status = "Resolved"

    def escalate(self):
        self.status = "Escalated"

    def to_dict(self):
        return {
            "ticket_id": self.ticket_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "assigned_agent_id": self.assigned_agent_id,
            "created_at": self.created_at,
        }
