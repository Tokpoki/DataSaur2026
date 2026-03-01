# 🔥 Freedom Intelligent Routing Engine (FIRE)

AI-powered backend system for automatic processing and routing of customer support tickets.

Developed for hackathon challenge.

---

## 📌 Project Overview

FIRE automatically:

1. Analyzes incoming customer tickets using LLM (Gemini)
2. Classifies issue type, sentiment, priority, language
3. Performs geo-normalization
4. Applies strict business rules
5. Assigns the most suitable manager
6. Balances workload (Round Robin logic)
7. Detects and filters spam

---

## 🧠 AI Capabilities

For each ticket the system extracts:

- Issue Type  
- Sentiment  
- Priority Score (1–10)  
- Language (RU / KZ / ENG)  
- Summary  
- Recommendation  
- Spam detection  

Spam tickets are stored but NOT assigned to managers.

---

## ⚙️ Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Gemini API (Google Generative AI)
- Streamlit (UI)
- Pandas
- Plotly

---

## 🗂 Project Structure

app/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── routers/
│ └── tickets.py
├── services/
│ ├── ai_service.py
│ ├── assignment.py
│ ├── geo_services.py
│ └── geocode_service.py
│
ui.py
importdb.py
---
## 🛠 Setup Instructions

### 1️⃣ Clone repository
git clone https://github.com/Tokpoki/fire-routing-engine.git

cd fire-routing-engine
---
### 2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate (Windows)
---
### 3️⃣ Install dependencies

pip install -r requirements.txt
Or manually:
pip install fastapi uvicorn sqlalchemy psycopg2-binary pandas streamlit plotly google-generativeai python-dotenv
---
### 4️⃣ Setup PostgreSQL
Create database:
CREATE DATABASE fire_db;
---
### 5️⃣ Configure environment variables

Create `.env` file:
GEMINI_API_KEY=your_api_key_here

Do NOT commit `.env` to GitHub.
---
### 6️⃣ Import initial data (tickets)
python importdb.py
---

## 🚀 Run Backend
uvicorn app.main:app --reload
Swagger available at:
http://127.0.0.1:8000/docs

---

## 🎛 Run UI
Available at:
http://localhost:8501
---

## 📊 Features

- Process single ticket
- Process all tickets
- Spam filtering
- Skill-based routing
- VIP & Priority rules
- Language filtering
- Geo-based office selection
- Workload balancing
- Interactive dashboard

---

## 🧹 Reset Database (optional)


TRUNCATE TABLE assignments RESTART IDENTITY CASCADE;
TRUNCATE TABLE ai_analysis RESTART IDENTITY CASCADE;
TRUNCATE TABLE tickets RESTART IDENTITY CASCADE;
UPDATE managers SET current_load = 0;

---

## 🏆 Business Rules Implemented

- VIP & Priority → only managers with VIP skill
- Change Data → only "Глав спец"
- Language KZ / ENG → manager must have language skill
- Spam → stored but not assigned
- Nearest office selection
- Fallback 50/50 (Astana / Almaty)
- Load balancing

---

## 👨‍💻 Author

Developed as part of FIRE Hackathon challenge.
