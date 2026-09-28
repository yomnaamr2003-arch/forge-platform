from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Float
)
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(180), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # "user" or "admin"
    created_at = Column(DateTime, default=datetime.utcnow)

    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    service_requests = relationship("ServiceRequest", back_populates="user", cascade="all, delete-orphan")


class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(160), nullable=False)
    category = Column(String(80), nullable=False)
    level = Column(String(40), nullable=False)  # Beginner / Intermediate / Advanced
    duration_weeks = Column(Integer, default=4)
    description = Column(Text, default="")
    modules = Column(Text, default="[]")  # JSON list of module titles
    tools = Column(Text, default="[]")  # JSON list of tool tags
    created_at = Column(DateTime, default=datetime.utcnow)

    enrollments = relationship("Enrollment", back_populates="program", cascade="all, delete-orphan")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    status = Column(String(20), default="active")  # active / completed
    completed_modules = Column(Text, default="[]")  # JSON list of module indices
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="enrollments")
    program = relationship("Program", back_populates="enrollments")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False)
    category = Column(String(80), nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    requests = relationship("ServiceRequest", back_populates="service", cascade="all, delete-orphan")


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    message = Column(Text, default="")
    status = Column(String(20), default="pending")  # pending / in_progress / resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="service_requests")
    service = relationship("Service", back_populates="requests")
