"""Persist submitted events and consult the shared installation history."""
from datetime import datetime, timedelta, timezone
import sqlite3
import streamlit as st
from history_store import HistoryStore

PENDING_KEY = "history_pending"


def render_history(progress=None):
    pending = st.session_state.setdefault(PENDING_KEY, [])
    if progress is not None:
        pending.extend(progress.pending_events)
        progress.pending_events.clear()
    store = HistoryStore()
    try:
        store.save_events(pending)
        pending.clear()
    except (sqlite3.Error, OSError):
        st.warning("Histórico indisponível. As tentativas pendentes serão reenviadas "
                   "na próxima interação enquanto esta sessão permanecer aberta.")
    with st.expander("Histórico de tentativas"):
        st.caption("Últimas 100 tentativas desta instalação, compartilhadas entre sessões. "
                   "Horários de Brasília. O histórico não restaura o exercício em andamento.")
        image_key = None
        if progress is not None:
            scope = st.selectbox("Consultar histórico", ("Todas as imagens", "Imagem atual"),
                                  key="history_scope")
            if scope == "Imagem atual":
                image_key = progress.identity
        try:
            rows = store.list_attempts(image_key)
        except (sqlite3.Error, OSError):
            st.info("Não foi possível consultar o histórico agora.")
            return
        if not rows:
            st.info("Nenhuma tentativa registrada neste filtro.")
            return
        outcomes = {"correct": "Correta", "incorrect": "Incorreta", "invalid": "Inválida"}
        st.dataframe([{
            "Data (Brasília)": datetime.fromisoformat(row["created_at"]).astimezone(
                timezone(timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M:%S"),
            "Imagem": row["image_key"][:12], "Exercício": row["run_id"][:8],
            "Dimensões": f"{row['width']} x {row['height']}",
            "Quadrante": f"Q{row['quadrant']}", "Resposta": row["answer_json"],
            "Resultado": outcomes[row["outcome"]], "Feedback": row["feedback"],
            "Concluídos": row["completed"],
        } for row in rows], hide_index=True, width="stretch")
