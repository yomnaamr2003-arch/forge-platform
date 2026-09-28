# Forge — Integrated Technology Learning & Services Platform

A full-stack web platform combining technology programs, learning resources, service requests,
user accounts, course enrollment, progress tracking, and an administrative dashboard — built
for the "Integrated Technology Learning & Services Platform" internship brief.

## Design

The visual identity is an original "engineering blueprint" theme: a deep graphite base,
a hairline blueprint grid, an ember-orange primary accent and a circuit-teal secondary accent,
set in Space Grotesk (headings) and IBM Plex Mono (UI/body) — chosen to reflect the
subject matter (code, circuits, schematics) rather than a generic template.

## Stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite, JWT auth (python-jose), bcrypt password hashing
- **Frontend:** Vanilla HTML5, CSS3, JavaScript (no framework, no build step)
- **API:** REST, JSON — documented automatically at `/docs` (Swagger UI) once the backend is running

## Project structure

```
forge-platform/
├── backend/
│   ├── main.py          # FastAPI app & all REST routes
│   ├── models.py        # SQLAlchemy models (User, Program, Enrollment, Service, ServiceRequest)
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── auth.py           # Password hashing + JWT auth dependencies
│   ├── database.py       # SQLite/SQLAlchemy session setup
│   ├── seed.py            # Synthetic demo data (5 programs, 6 services, 1 admin)
│   └── requirements.txt
└── frontend/
    ├── index.html         # Public landing page + program catalog + service catalog
    ├── login.html / register.html
    ├── course.html         # Program detail + enroll action
    ├── dashboard.html      # User dashboard: progress, module tracking, service requests
    ├── admin.html          # Admin dashboard: CRUD, request queue, analytics, users
    ├── css/style.css
    └── js/api.js           # Fetch-based API client + session/auth helpers
```

## Setup

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py                  # creates forge.db with demo programs, services & an admin user
uvicorn main:app --reload       # runs on http://127.0.0.1:8000
```

Seeded admin login: **admin@forge.dev** / **admin123**

API docs (Swagger UI): http://127.0.0.1:8000/docs

### 2. Frontend

The frontend is static — no build step. Serve it with any static server so the browser
treats it as a real origin (recommended over opening the file directly):

```bash
cd frontend
python -m http.server 5500
```

Then open http://127.0.0.1:5500 in your browser. The frontend calls the API at
`http://127.0.0.1:8000/api` (see `API_BASE` in `frontend/js/api.js` — change this if you
deploy the backend elsewhere).

## Features implemented (per the brief)

- [x] Responsive public website
- [x] Program and service catalog (filterable by category)
- [x] User registration and login (JWT, bcrypt-hashed passwords)
- [x] Course enrollment
- [x] Learning progress tracking (per-module checklist, computed % complete)
- [x] Service request module (submit + track status: pending / in progress / resolved)
- [x] User dashboard (overview stats, my programs, my requests)
- [x] Admin dashboard (analytics, full CRUD on programs & services, request queue, user directory)
- [x] CRUD operations (programs, services, service requests)
- [x] Database integration (SQLite via SQLAlchemy ORM)
- [x] REST API (`/api/...`, versionable, documented via OpenAPI)
- [x] Basic analytics (totals, active/completed enrollments, requests by status, enrollments by category)
- [x] README and project documentation

## Notes

- The first user to register automatically becomes an admin (convenience for local grading/demo);
  every user after that registers with the standard `user` role.
- All data is synthetic/seeded — no production or private data is used, per the brief's hints.
- Role-based access is enforced server-side: program/service CRUD and the request/user admin
  endpoints require an admin JWT, not just a hidden UI element.
