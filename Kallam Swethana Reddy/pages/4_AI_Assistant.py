"""AI Assistant — local Ollama llama3.2 chat with database-aware context."""
from __future__ import annotations

import uuid

import streamlit as st

from database import (
    init_db, get_settings, add_chat_message, get_chat_history, clear_chat_history,
)
from ollama_backend import answer_with_context, ollama_available, OLLAMA_MODEL
from auth_ui import require_login, render_user_sidebar
from utils import inject_css, render_sidebar_brand, page_header

st.set_page_config(page_title="AI Assistant • CIH", page_icon="🤖", layout="wide")
init_db()
inject_css()
user = require_login()
user_id = user["id"]
settings = get_settings(user_id)
render_sidebar_brand(settings.get("company_name"))
render_user_sidebar()
page_header("AI Assistant",
            f"Chat with local {OLLAMA_MODEL} — grounded in your project database.",
            icon="🤖")

# session
if "chat_session_id" not in st.session_state:
    st.session_state["chat_session_id"] = str(uuid.uuid4())
session_id = st.session_state["chat_session_id"]

ok, msg = ollama_available()
if not ok:
    st.warning(msg)

# controls
c1, c2 = st.columns([3, 1])
with c2:
    if st.button("🗑️ Clear chat", use_container_width=True):
        clear_chat_history(user_id, session_id)
        st.rerun()

# history
history = get_chat_history(user_id, session_id)
for m in history:
    role_cls = "cih-chat-user" if m["role"] == "user" else "cih-chat-ai"
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])
        if m["role"] == "assistant" and m.get("used_context"):
            st.caption("🔎 Answer grounded in SQLite project data.")

prompt = st.chat_input("Ask about your projects, budgets, materials, safety, planning…")
if prompt:
    add_chat_message(user_id, session_id, "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # send previous turns as chat history for continuity
    hist_msgs = [{"role": m["role"], "content": m["content"]} for m in history]
    with st.chat_message("assistant"):
        with st.spinner("Thinking with llama3.2…"):
            answer, used_ctx, intent = answer_with_context(prompt, user_id, history=hist_msgs)
        st.markdown(answer)
        if used_ctx:
            st.caption(f"🔎 Grounded via intent `{intent.name}` (confidence {intent.confidence:.2f}).")

    add_chat_message(user_id, session_id, "assistant", answer, used_context=used_ctx)
    st.rerun()

st.markdown("---")
with st.expander("💡 Example questions"):
    st.markdown(
        "- How many active projects do we have?\n"
        "- What is the total budget across all projects?\n"
        "- Show me details of project *Skyline Tower*.\n"
        "- Estimate materials for 12x9x3 building, 2 floors, premium quality.\n"
        "- What are the current material rates?\n"
        "- Which projects are on hold?\n"
    )
