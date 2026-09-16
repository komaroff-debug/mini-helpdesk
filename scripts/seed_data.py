"""
Populates the database with a handful of users, categories, and tickets so
the API and dashboard have something realistic to show.

Run with:  python -m scripts.seed_data
"""
from app.database import Base, SessionLocal, engine
from app.models.category import Category
from app.models.comment import Comment
from app.models.status_history import StatusHistory
from app.models.ticket import Ticket
from app.models.user import User
from app.security import hash_password


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(User).first():
        print("Database already has data, skipping seed.")
        return

    admin = User(
        email="admin@example.com",
        password_hash=hash_password("admin123"),
        full_name="Admin User",
        role="admin",
    )
    agent = User(
        email="agent@example.com",
        password_hash=hash_password("agent123"),
        full_name="Alex Agent",
        role="agent",
    )
    client = User(
        email="client@example.com",
        password_hash=hash_password("client123"),
        full_name="Casey Client",
        role="client",
    )
    db.add_all([admin, agent, client])
    db.commit()

    billing = Category(name="Billing")
    technical = Category(name="Technical")
    db.add_all([billing, technical])
    db.commit()

    ticket1 = Ticket(
        title="Can't log in to my account",
        description="Getting an error every time I try to sign in.",
        status="in_progress",
        priority="high",
        category_id=technical.id,
        created_by=client.id,
        assigned_to=agent.id,
    )
    ticket2 = Ticket(
        title="Refund not received",
        description="I cancelled my subscription two weeks ago.",
        status="open",
        priority="medium",
        category_id=billing.id,
        created_by=client.id,
    )
    db.add_all([ticket1, ticket2])
    db.commit()

    db.add(
        StatusHistory(
            ticket_id=ticket1.id,
            old_status="open",
            new_status="in_progress",
            changed_by=agent.id,
        )
    )
    db.add(
        Comment(
            ticket_id=ticket1.id,
            author_id=agent.id,
            body="Looking into this now, could you try resetting your password?",
        )
    )
    db.commit()
    db.close()
    print("Seed data created.")
    print("Login as: admin@example.com / admin123")
    print("          agent@example.com / agent123")
    print("          client@example.com / client123")


if __name__ == "__main__":
    run()
