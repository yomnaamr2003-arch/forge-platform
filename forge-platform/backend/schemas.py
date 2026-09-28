from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


# ---------- Auth / User ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Program ----------
class ProgramCreate(BaseModel):
    title: str
    category: str
    level: str
    duration_weeks: int = 4
    description: str = ""
    modules: List[str] = []
    tools: List[str] = []


class ProgramUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    duration_weeks: Optional[int] = None
    description: Optional[str] = None
    modules: Optional[List[str]] = None
    tools: Optional[List[str]] = None


class ProgramOut(BaseModel):
    id: int
    title: str
    category: str
    level: str
    duration_weeks: int
    description: str
    modules: List[str]
    tools: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Enrollment ----------
class EnrollmentCreate(BaseModel):
    program_id: int


class EnrollmentOut(BaseModel):
    id: int
    program_id: int
    program_title: str
    status: str
    completed_modules: List[int]
    total_modules: int
    progress_percent: float
    enrolled_at: datetime

    class Config:
        from_attributes = True


class ModuleToggle(BaseModel):
    module_index: int
    completed: bool


# ---------- Service ----------
class ServiceCreate(BaseModel):
    name: str
    category: str
    description: str = ""


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None


class ServiceOut(BaseModel):
    id: int
    name: str
    category: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Service Request ----------
class ServiceRequestCreate(BaseModel):
    service_id: int
    message: str = ""


class ServiceRequestStatusUpdate(BaseModel):
    status: str


class ServiceRequestOut(BaseModel):
    id: int
    service_id: int
    service_name: str
    user_id: int
    user_name: str
    message: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------- Analytics ----------
class AnalyticsOut(BaseModel):
    total_users: int
    total_programs: int
    total_services: int
    total_enrollments: int
    active_enrollments: int
    completed_enrollments: int
    pending_requests: int
    resolved_requests: int
    enrollments_by_category: dict
    requests_by_status: dict
