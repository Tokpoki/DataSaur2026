from sqlalchemy.orm import Session
from ..models import (
    Ticket,
    AIAnalysis,
    Assignment,
    Manager,
    BusinessUnit,
)
from ..services.ai_service import analyze_text
from ..services.geo_services import find_nearest_office
from ..services.geocode_service import geocode_address
import random
import logging

logger = logging.getLogger(__name__)


def process_ticket(ticket_id: int, db: Session):

    try:
        logger.info(f"Processing ticket {ticket_id}")

        # 1️⃣ Проверка: уже обработан?
        existing_assignment = db.query(Assignment).filter(
            Assignment.ticket_id == ticket_id
        ).first()

        if existing_assignment:
            return {"message": "Ticket already processed"}

        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

        if not ticket:
            raise Exception("Ticket not found")

        # 2️⃣ AI анализ (если ещё нет)
        ai = db.query(AIAnalysis).filter(
            AIAnalysis.ticket_id == ticket.id
        ).first()

        if not ai:
            result = analyze_text(ticket.description or "")

            ai = AIAnalysis(
                ticket_id=ticket.id,
                issue_type=result["issue_type"],
                sentiment=result["sentiment"],
                priority_score=result["priority_score"],
                language=result["language"],
                summary=result["summary"],
                recommendation=result["recommendation"],
            )

            db.add(ai)
            db.commit()
            db.refresh(ai)

        # 🔥 СПАМ — НЕ НАЗНАЧАЕМ МЕНЕДЖЕРА
        if ai.issue_type == "Спам":
            logger.info(f"Ticket {ticket.id} detected as spam. No assignment created.")
            return {
                "ticket_id": ticket.id,
                "status": "Spam detected",
                "message": "Ticket stored without assignment"
            }

        # 3️⃣ Гео-определение клиента
        office = None

        if ai.latitude and ai.longitude:
            office = find_nearest_office(
                db,
                float(ai.latitude),
                float(ai.longitude)
            )
        else:
            full_address = f"{ticket.street or ''} {ticket.house or ''}"
            lat, lon = geocode_address(full_address, ticket.city or "")

            if lat and lon:
                ai.latitude = str(lat)
                ai.longitude = str(lon)
                db.commit()
                office = find_nearest_office(db, lat, lon)

        # Fallback 50/50
        if not office:
            astana = db.query(BusinessUnit).filter(
                BusinessUnit.office_name.ilike("%астана%")
            ).first()

            almaty = db.query(BusinessUnit).filter(
                BusinessUnit.office_name.ilike("%алматы%")
            ).first()

            office = random.choice([o for o in [astana, almaty] if o])

        if not office:
            raise Exception("No office found")

        # 4️⃣ Фильтрация менеджеров
        managers = db.query(Manager).filter(
            Manager.office_name == office.office_name
        ).all()

        if not managers:
            raise Exception("No managers in this office")

        filtered = []

        for manager in managers:

            skills = manager.skills or ""

            # VIP / Priority
            if ticket.segment in ["VIP", "Priority"]:
                if "VIP" not in skills:
                    continue

            # Смена данных
            if ai.issue_type == "Смена данных":
                if manager.position != "Глав спец":
                    continue

            # Язык
            if ai.language == "KZ" and "KZ" not in skills:
                continue

            if ai.language == "ENG" and "ENG" not in skills:
                continue

            filtered.append(manager)

        # Fail-safe
        if not filtered:
            logger.warning("No managers passed filters. Using fallback.")
            filtered = managers

        # 5️⃣ Балансировка
        filtered_sorted = sorted(
            filtered,
            key=lambda m: m.current_load or 0
        )

        top_two = filtered_sorted[:2] if len(filtered_sorted) >= 2 else filtered_sorted

        if not top_two:
            raise Exception("No managers available")

        selected_manager = min(top_two, key=lambda m: m.current_load or 0)

        # 6️⃣ Создаём Assignment
        assignment = Assignment(
            ticket_id=ticket.id,
            manager_id=selected_manager.id
        )

        db.add(assignment)

        selected_manager.current_load = (selected_manager.current_load or 0) + 1

        db.commit()

        logger.info(
            f"Ticket {ticket.id} assigned to {selected_manager.full_name}"
        )

        return {
            "ticket_id": ticket.id,
            "office": office.office_name,
            "manager": selected_manager.full_name,
            "issue_type": ai.issue_type,
            "priority": ai.priority_score
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error processing ticket {ticket_id}: {str(e)}")
        raise


def process_all_tickets(db: Session):

    tickets = db.query(Ticket).all()

    results = []

    for ticket in tickets:
        try:
            result = process_ticket(ticket.id, db)
            results.append(result)
        except Exception as e:
            results.append({
                "ticket_id": ticket.id,
                "error": str(e)
            })

    return results