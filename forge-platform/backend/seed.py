"""Populate the database with synthetic demo data.
Run with: python seed.py
"""
import json
from database import SessionLocal, engine, Base
import models
from auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(models.Program).count() == 0:
    programs = [
        dict(
            title="Full-Stack Web Foundations", category="Web Development", level="Beginner",
            duration_weeks=6,
            description="Build responsive sites with HTML5, CSS3 and JavaScript, then connect them to a real backend.",
            modules=["HTML & Semantic Markup", "CSS Layout & Responsive Design", "JavaScript Fundamentals",
                     "Working with the DOM", "Fetching Data from an API", "Capstone: Build a Landing Page"],
            tools=["HTML5", "CSS3", "JavaScript", "Git"],
        ),
        dict(
            title="REST API Engineering", category="Backend Development", level="Intermediate",
            duration_weeks=5,
            description="Design and build production-style REST APIs with authentication, validation and a database.",
            modules=["API Design Principles", "Routing & Request Handling", "Databases & ORMs",
                     "Authentication & Authorization", "Testing & Documentation"],
            tools=["Python", "FastAPI", "SQLite", "REST API"],
        ),
        dict(
            title="Applied Data Structures", category="Computer Science", level="Intermediate",
            duration_weeks=8,
            description="Implement and apply the data structures and algorithms used in real software systems.",
            modules=["Arrays & Linked Lists", "Stacks & Queues", "Trees & Graphs",
                     "Sorting & Searching", "Complexity Analysis", "Interview Problem Sets"],
            tools=["Python", "Git", "GitHub"],
        ),
        dict(
            title="Cloud & DevOps Essentials", category="Infrastructure", level="Advanced",
            duration_weeks=6,
            description="Ship and operate applications with modern CI/CD, containers and version control workflows.",
            modules=["Git & GitHub Workflows", "Containers Basics", "CI/CD Pipelines",
                     "Environment Configuration", "Monitoring & Logging"],
            tools=["Git", "GitHub", "REST API"],
        ),
        dict(
            title="Databases & SQL in Practice", category="Data", level="Beginner",
            duration_weeks=4,
            description="Model, query and manage relational databases used behind real applications.",
            modules=["Relational Modeling", "Writing SQL Queries", "Joins & Aggregation", "Indexing & Performance"],
            tools=["SQLite", "PostgreSQL", "JSON"],
        ),
    ]
    for p in programs:
        db.add(models.Program(
            title=p["title"], category=p["category"], level=p["level"],
            duration_weeks=p["duration_weeks"], description=p["description"],
            modules=json.dumps(p["modules"]), tools=json.dumps(p["tools"]),
        ))
    db.commit()
    print(f"Seeded {len(programs)} programs.")

if db.query(models.Service).count() == 0:
    services = [
        dict(name="1:1 Career Mentorship", category="Mentorship",
             description="Book a session with an instructor to plan your learning path and review your portfolio."),
        dict(name="Code Review", category="Technical Support",
             description="Get a detailed review of a project or assignment before you submit it."),
        dict(name="Technical Support", category="Technical Support",
             description="Get help with environment setup, debugging, or tooling issues."),
        dict(name="Resume & Portfolio Review", category="Career Services",
             description="Have your resume and project portfolio reviewed by a careers advisor."),
        dict(name="Mock Technical Interview", category="Career Services",
             description="Practice a live coding interview and get structured feedback."),
        dict(name="Enterprise Training Request", category="Corporate",
             description="Request a custom cohort or workshop for your organization."),
    ]
    for s in services:
        db.add(models.Service(**s))
    db.commit()
    print(f"Seeded {len(services)} services.")

if db.query(models.User).filter(models.User.email == "admin@forge.dev").first() is None:
    db.add(models.User(
        name="Forge Admin", email="admin@forge.dev",
        password_hash=hash_password("admin123"), role="admin",
    ))
    db.commit()
    print("Seeded admin user: admin@forge.dev / admin123")

db.close()
print("Seeding complete.")
