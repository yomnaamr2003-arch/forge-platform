import json
from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func

import models
import schemas
from database import engine, get_db, Base
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, require_admin,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Forge Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def program_to_out(p: models.Program) -> schemas.ProgramOut:
    return schemas.ProgramOut(
        id=p.id, title=p.title, category=p.category, level=p.level,
        duration_weeks=p.duration_weeks, description=p.description,
        modules=json.loads(p.modules or "[]"), tools=json.loads(p.tools or "[]"),
        created_at=p.created_at,
    )


def enrollment_to_out(e: models.Enrollment) -> schemas.EnrollmentOut:
    modules = json.loads(e.program.modules or "[]")
    completed = json.loads(e.completed_modules or "[]")
    total = len(modules) or 1
    pct = round(len(completed) / total * 100, 1) if modules else 0.0
    return schemas.EnrollmentOut(
        id=e.id, program_id=e.program_id, program_title=e.program.title,
        status=e.status, completed_modules=completed, total_modules=len(modules),
        progress_percent=pct, enrolled_at=e.enrolled_at,
    )


def request_to_out(r: models.ServiceRequest) -> schemas.ServiceRequestOut:
    return schemas.ServiceRequestOut(
        id=r.id, service_id=r.service_id, service_name=r.service.name,
        user_id=r.user_id, user_name=r.user.name, message=r.message,
        status=r.status, created_at=r.created_at, updated_at=r.updated_at,
    )


# ======================= AUTH =======================
@app.post("/api/auth/register", response_model=schemas.Token, status_code=201)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    is_first_user = db.query(models.User).count() == 0
    user = models.User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="admin" if is_first_user else "user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    return schemas.Token(access_token=token, user=user)


@app.post("/api/auth/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = create_access_token({"sub": str(user.id)})
    return schemas.Token(access_token=token, user=user)


@app.get("/api/auth/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user


# ======================= PROGRAMS =======================
@app.get("/api/programs", response_model=List[schemas.ProgramOut])
def list_programs(category: str = None, level: str = None, db: Session = Depends(get_db)):
    q = db.query(models.Program)
    if category:
        q = q.filter(models.Program.category == category)
    if level:
        q = q.filter(models.Program.level == level)
    return [program_to_out(p) for p in q.order_by(models.Program.created_at.desc()).all()]


@app.get("/api/programs/{program_id}", response_model=schemas.ProgramOut)
def get_program(program_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Program).get(program_id)
    if not p:
        raise HTTPException(status_code=404, detail="Program not found")
    return program_to_out(p)


@app.post("/api/programs", response_model=schemas.ProgramOut, status_code=201)
def create_program(payload: schemas.ProgramCreate, db: Session = Depends(get_db),
                    admin: models.User = Depends(require_admin)):
    p = models.Program(
        title=payload.title, category=payload.category, level=payload.level,
        duration_weeks=payload.duration_weeks, description=payload.description,
        modules=json.dumps(payload.modules), tools=json.dumps(payload.tools),
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return program_to_out(p)


@app.put("/api/programs/{program_id}", response_model=schemas.ProgramOut)
def update_program(program_id: int, payload: schemas.ProgramUpdate, db: Session = Depends(get_db),
                    admin: models.User = Depends(require_admin)):
    p = db.query(models.Program).get(program_id)
    if not p:
        raise HTTPException(status_code=404, detail="Program not found")
    data = payload.dict(exclude_unset=True)
    for field in ("modules", "tools"):
        if field in data:
            data[field] = json.dumps(data[field])
    for k, v in data.items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return program_to_out(p)


@app.delete("/api/programs/{program_id}", status_code=204)
def delete_program(program_id: int, db: Session = Depends(get_db),
                    admin: models.User = Depends(require_admin)):
    p = db.query(models.Program).get(program_id)
    if not p:
        raise HTTPException(status_code=404, detail="Program not found")
    db.delete(p)
    db.commit()
    return None


# ======================= ENROLLMENTS =======================
@app.get("/api/enrollments/me", response_model=List[schemas.EnrollmentOut])
def my_enrollments(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    rows = db.query(models.Enrollment).filter(models.Enrollment.user_id == user.id).all()
    return [enrollment_to_out(e) for e in rows]


@app.post("/api/enrollments", response_model=schemas.EnrollmentOut, status_code=201)
def enroll(payload: schemas.EnrollmentCreate, db: Session = Depends(get_db),
           user: models.User = Depends(get_current_user)):
    program = db.query(models.Program).get(payload.program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    existing = db.query(models.Enrollment).filter(
        models.Enrollment.user_id == user.id,
        models.Enrollment.program_id == payload.program_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled in this program")
    e = models.Enrollment(user_id=user.id, program_id=payload.program_id)
    db.add(e)
    db.commit()
    db.refresh(e)
    return enrollment_to_out(e)


@app.patch("/api/enrollments/{enrollment_id}/module", response_model=schemas.EnrollmentOut)
def toggle_module(enrollment_id: int, payload: schemas.ModuleToggle, db: Session = Depends(get_db),
                   user: models.User = Depends(get_current_user)):
    e = db.query(models.Enrollment).get(enrollment_id)
    if not e or e.user_id != user.id:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    completed = set(json.loads(e.completed_modules or "[]"))
    if payload.completed:
        completed.add(payload.module_index)
    else:
        completed.discard(payload.module_index)
    e.completed_modules = json.dumps(sorted(completed))
    total_modules = len(json.loads(e.program.modules or "[]"))
    e.status = "completed" if total_modules and len(completed) >= total_modules else "active"
    db.commit()
    db.refresh(e)
    return enrollment_to_out(e)


# ======================= SERVICES =======================
@app.get("/api/services", response_model=List[schemas.ServiceOut])
def list_services(db: Session = Depends(get_db)):
    return db.query(models.Service).order_by(models.Service.category).all()


@app.post("/api/services", response_model=schemas.ServiceOut, status_code=201)
def create_service(payload: schemas.ServiceCreate, db: Session = Depends(get_db),
                    admin: models.User = Depends(require_admin)):
    s = models.Service(**payload.dict())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@app.put("/api/services/{service_id}", response_model=schemas.ServiceOut)
def update_service(service_id: int, payload: schemas.ServiceUpdate, db: Session = Depends(get_db),
                    admin: models.User = Depends(require_admin)):
    s = db.query(models.Service).get(service_id)
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s


@app.delete("/api/services/{service_id}", status_code=204)
def delete_service(service_id: int, db: Session = Depends(get_db),
                    admin: models.User = Depends(require_admin)):
    s = db.query(models.Service).get(service_id)
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(s)
    db.commit()
    return None


# ======================= SERVICE REQUESTS =======================
@app.get("/api/service-requests/me", response_model=List[schemas.ServiceRequestOut])
def my_requests(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    rows = db.query(models.ServiceRequest).filter(models.ServiceRequest.user_id == user.id).all()
    return [request_to_out(r) for r in rows]


@app.post("/api/service-requests", response_model=schemas.ServiceRequestOut, status_code=201)
def create_request(payload: schemas.ServiceRequestCreate, db: Session = Depends(get_db),
                    user: models.User = Depends(get_current_user)):
    service = db.query(models.Service).get(payload.service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    r = models.ServiceRequest(user_id=user.id, service_id=payload.service_id, message=payload.message)
    db.add(r)
    db.commit()
    db.refresh(r)
    return request_to_out(r)


@app.get("/api/service-requests", response_model=List[schemas.ServiceRequestOut])
def all_requests(db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    rows = db.query(models.ServiceRequest).order_by(models.ServiceRequest.created_at.desc()).all()
    return [request_to_out(r) for r in rows]


@app.patch("/api/service-requests/{request_id}/status", response_model=schemas.ServiceRequestOut)
def update_request_status(request_id: int, payload: schemas.ServiceRequestStatusUpdate,
                           db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    r = db.query(models.ServiceRequest).get(request_id)
    if not r:
        raise HTTPException(status_code=404, detail="Request not found")
    r.status = payload.status
    r.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(r)
    return request_to_out(r)


# ======================= ADMIN: USERS =======================
@app.get("/api/admin/users", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    return db.query(models.User).order_by(models.User.created_at.desc()).all()


# ======================= ANALYTICS =======================
@app.get("/api/admin/analytics", response_model=schemas.AnalyticsOut)
def analytics(db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    total_users = db.query(models.User).count()
    total_programs = db.query(models.Program).count()
    total_services = db.query(models.Service).count()
    total_enrollments = db.query(models.Enrollment).count()
    active_enrollments = db.query(models.Enrollment).filter(models.Enrollment.status == "active").count()
    completed_enrollments = db.query(models.Enrollment).filter(models.Enrollment.status == "completed").count()
    pending_requests = db.query(models.ServiceRequest).filter(models.ServiceRequest.status == "pending").count()
    resolved_requests = db.query(models.ServiceRequest).filter(models.ServiceRequest.status == "resolved").count()

    cat_rows = (
        db.query(models.Program.category, func.count(models.Enrollment.id))
        .join(models.Enrollment, models.Enrollment.program_id == models.Program.id)
        .group_by(models.Program.category)
        .all()
    )
    enrollments_by_category = {c: n for c, n in cat_rows}

    status_rows = (
        db.query(models.ServiceRequest.status, func.count(models.ServiceRequest.id))
        .group_by(models.ServiceRequest.status)
        .all()
    )
    requests_by_status = {s: n for s, n in status_rows}

    return schemas.AnalyticsOut(
        total_users=total_users, total_programs=total_programs, total_services=total_services,
        total_enrollments=total_enrollments, active_enrollments=active_enrollments,
        completed_enrollments=completed_enrollments, pending_requests=pending_requests,
        resolved_requests=resolved_requests, enrollments_by_category=enrollments_by_category,
        requests_by_status=requests_by_status,
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}
