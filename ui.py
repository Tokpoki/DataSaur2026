import streamlit as st
import pandas as pd
import requests
import psycopg2
import plotly.express as px

API_URL = "http://127.0.0.1:8000"

DB_CONFIG = {
    "host": "localhost",
    "database": "fire_db",
    "user": "postgres",
    "password": "root",
    "port": "5432",
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def load_tickets():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM tickets ORDER BY id", conn)
    conn.close()
    return df


def load_ai():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM ai_analysis ORDER BY id", conn)
    conn.close()
    return df


def load_assignments():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT a.id,
               a.ticket_id,
               m.full_name as manager,
               m.position,
               m.office_name
        FROM assignments a
        JOIN managers m ON a.manager_id = m.id
        ORDER BY a.id
    """, conn)
    conn.close()
    return df


st.set_page_config(page_title="FIRE Control Panel", layout="wide")
st.title("🔥 FIRE Control Panel")

# --- Управление ---
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Обработать ВСЕ тикеты"):
        requests.post(f"{API_URL}/tickets/process-all")
        st.success("Все тикеты обработаны")
        st.rerun()

tickets_df = load_tickets()

with col2:
    ticket_ids = tickets_df["id"].tolist()
    selected_ticket = st.selectbox("Выбери тикет", ticket_ids)

    if st.button("⚡ Обработать выбранный"):
        requests.post(f"{API_URL}/tickets/{selected_ticket}/process")
        st.success(f"Тикет {selected_ticket} обработан")
        st.rerun()

st.divider()

# --- Метрики ---
ai_df = load_ai()
assign_df = load_assignments()

col1, col2, col3 = st.columns(3)

col1.metric("Всего тикетов", len(tickets_df))
col2.metric("AI обработано", len(ai_df))
col3.metric("Назначено менеджерам", len(assign_df))

st.divider()

# --- График типов ---
if not ai_df.empty:
    st.subheader("📊 Распределение типов обращений")

    fig = px.histogram(
        ai_df,
        x="issue_type",
        title="Типы обращений"
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Таблица тикетов ---
st.subheader("📋 Tickets")
st.dataframe(tickets_df, use_container_width=True)

st.divider()

# --- AI Analysis ---
st.subheader("🧠 AI Analysis")
st.dataframe(ai_df, use_container_width=True)

st.divider()

# --- Assignments ---
st.subheader("👨‍💼 Assignments")
st.dataframe(assign_df, use_container_width=True)