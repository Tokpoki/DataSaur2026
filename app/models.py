from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.sql import func


class BusinessUnit(Base):
    __tablename__ = "business_units"

    id = Column(Integer, primary_key=True, index=True)
    office_name = Column(String(150), unique=True, nullable=False)
    address = Column(Text, nullable=False)
    latitude = Column(String)
    longitude = Column(String)


class Manager(Base):
    __tablename__ = "managers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150))
    position = Column(String(100))
    office_name = Column(String(150))
    skills = Column(Text)
    current_load = Column(Integer)


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    client_guid = Column(String(100))
    gender = Column(String(20))
    birth_date = Column(TIMESTAMP)
    description = Column(Text)
    attachment = Column(Text)
    segment = Column(String(20))
    country = Column(String(100))
    region = Column(String(100))
    city = Column(String(100))
    street = Column(String(150))
    house = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    issue_type = Column(String(50))
    sentiment = Column(String(20))
    priority_score = Column(Integer)
    language = Column(String(10))
    summary = Column(Text)
    recommendation = Column(Text)
    latitude = Column(String)
    longitude = Column(String)


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    manager_id = Column(Integer, ForeignKey("managers.id"))
    assigned_at = Column(TIMESTAMP, server_default=func.now())