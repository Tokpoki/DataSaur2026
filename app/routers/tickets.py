from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Ticket
from ..schemas import TicketResponse
from ..services.ai_service import analyze_text
from ..services.assignment import process_ticket, process_all_tickets
from ..services.geocode_service import fill_office_coordinates


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)


# 🔥 Обработка одного тикета
@router.post("/{ticket_id}/process")
def process(ticket_id: int, db: Session = Depends(get_db)):
    return process_ticket(ticket_id, db)


# 🔥 Обработка всех тикетов
@router.post("/process-all")
def process_all(db: Session = Depends(get_db)):
    return process_all_tickets(db)


# 🔥 Тест Gemini
@router.post("/test-gemini")
def test_gemini():
    return analyze_text(
        "Hello, I would like to clarify how to change my email address in my profile"
    )


# 🔥 Тест AI
@router.post("/test-ai")
def test_ai():
    result = analyze_text(
        "У меня не работает мобильное приложение, срочно помогите!"
    )
    return {"ai_response": result}


# 🔥 Геокодинг офисов
@router.post("/geocode-offices")
def geocode_offices(db: Session = Depends(get_db)):
    fill_office_coordinates(db)
    return {"message": "Geocoding completed"}


# 🔥 Получить список тикетов
@router.get("/", response_model=List[TicketResponse])
def get_tickets(db: Session = Depends(get_db)):
    return db.query(Ticket).limit(50).all()


# 🔥 Получить один тикет
@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket