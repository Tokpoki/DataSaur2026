from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TicketBase(BaseModel):
    client_guid: Optional[str]
    gender: Optional[str]
    birth_date: Optional[datetime]
    description: Optional[str]
    attachment: Optional[str]
    segment: Optional[str]
    country: Optional[str]
    region: Optional[str]
    city: Optional[str]
    street: Optional[str]
    house: Optional[str]


class TicketResponse(TicketBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # для SQLAlchemy