"""Global Construction AI assistant, available from every application page."""
from __future__ import annotations

import streamlit as st

from repository import get_repository
from services import ai_chat

def _get_suggestions(page: str) -> list[tuple[str, str]]:
    suggestions = {
        "Dashboard": [
            ("📊 Project Summary", "Summarize current project status"),
            ("⚠️ Risk Overview", "Show current project risks"),
            ("📈 Progress Analysis", "Analyze project progress"),
            ("💰 Budget Status", "Analyze budget status"),
        ],

        "Project Portfolio": [
            ("🏗️ Portfolio Overview", "Summarize all projects"),
            ("📊 Project Comparison", "Compare project performance"),
            ("⚠️ Portfolio Risks", "Identify portfolio level risks"),
            ("📈 Overall Progress", "Analyze portfolio progress"),
        ],

        "AI Actions": [
            ("🤖 AI Summary", "Generate AI project summary"),
            ("🔮 Risk Prediction", "Predict upcoming project risks"),
            ("🧱 Material Estimate", "Estimate required materials"),
            ("📋 Daily Report", "Generate daily construction report"),
        ],

        "Analytics": [
            ("📊 Performance Analysis", "Analyze project performance"),
            ("📈 Progress Trends", "Analyze progress trends"),
            ("💰 Cost Analysis", "Analyze project costs"),
            ("⚠️ Issues Detection", "Find project issues"),
        ],

        "Settings": [
            ("⚙️ System Overview", "Explain system configuration"),
            ("🤖 AI Capabilities", "Explain available AI features"),
            ("📊 Usage Summary", "Summarize assistant usage"),
            ("🔧 Recommendations", "Suggest system improvements"),
        ],

        "Project Workspace": [
            ("🏗️ Project Status", "Summarize current workspace project"),
            ("🧱 Resource Analysis", "Analyze project resources"),
            ("⚠️ Safety Check", "Analyze safety conditions"),
            ("📅 Schedule Review", "Review project schedule"),
        ],
    }

    return suggestions.get(page, suggestions["Dashboard"])


def _build_context() -> dict:
    """Build the current page context without changing application state."""
    repo = get_repository()
    context = {"page": st.session_state.get("page", "Dashboard")}
    project_id = st.session_state.get("current_project_id")

    if project_id:
        project = repo.get_project(project_id)
        if project:
            context["project"] = project
            return context

    context["projects"] = repo.list_projects()
    return context


def _context_summary(context: dict) -> str:
    if context.get("project"):
        project = context["project"]
        return f"{context['page']} · {project.name} · {project.progress:.0f}% complete"
    return f"{context['page']} · Portfolio · {len(context.get('projects', []))} projects"


def _get_chat_history() -> list[dict[str, str]]:
    """Return the persistent conversation for this browser session."""
    return st.session_state.setdefault("ai_chat_history", [])


def _ask(prompt: str, context: dict) -> None:
    """Add a user question and its response to the persistent conversation."""
    history = _get_chat_history()
    history.append({"role": "user", "content": prompt})
    try:
        response = ai_chat(prompt, context=context)
    except Exception:
        response = (
            "I couldn't complete that request right now. Please try again in a moment."
        )
    history.append({"role": "assistant", "content": response})

    # Keep the session lightweight while retaining a useful conversation window.
    if len(history) > 40:
        del history[:-40]


@st.dialog("Construction AI", width="small")
def _render_assistant_dialog(context: dict) -> None:
    """Render a native modal so the current workspace remains untouched behind it."""
    # st.markdown("## 🏗️ Construction AI Copilot")

    st.caption(f"📍 {_context_summary(context)}")

    st.divider()

    history = _get_chat_history()

    if not history:

        page = st.session_state.get("page", "Dashboard")

        st.write("### Suggested Questions")

        suggestions = _get_suggestions(page)

        for i in range(0, len(suggestions), 2):
            cols = st.columns(2)

            for col, item in zip(cols, suggestions[i:i+2]):
                label, prompt = item

                with col:
                    if st.button(
                        label,
                        use_container_width=True,
                        key=f"ai_suggestion_{i}_{label}"
                    ):
                        _ask(prompt, context)
                        st.rerun()

        st.divider()

    st.markdown(
        '<div class="ai-history">',
        unsafe_allow_html=True,
    )

    for message in history:
        role = "assistant" if message["role"] in {"assistant", "ai"} else "user"
        with st.chat_message(role):
            st.markdown(message["content"])

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    input_col, send_col = st.columns([5, 1])

    with input_col:
        prompt = st.text_input(
            "Ask Construction AI",
            key="construction_ai_prompt",
            label_visibility="collapsed",
            placeholder="Ask Construction AI..."
        )

    with send_col:
        send = st.button("➤", key="send_ai_prompt")

    if send and prompt:
        _ask(prompt, context)
        st.rerun()

    clear_col, close_col = st.columns(2)
    with clear_col:
        if st.button("Clear conversation", key="ai_clear_conversation", use_container_width=True):
            st.session_state["ai_chat_history"] = []
            st.rerun()
    with close_col:
        # if st.button("Close assistant", key="ai_close_assistant", use_container_width=True):
        #     st.rerun()
        if st.button("Close assistant", key="ai_close_assistant"):
            st.session_state["ai_open"] = False
            st.rerun()


def render_ai_assistant() -> None:
    """Render the fixed launcher shared by all routes."""
    st.markdown(
        """
        <style>
        .st-key-construction_ai_launcher {
            position: fixed;
            right: 1.5rem;
            bottom: 1.5rem;
            z-index: 1000;
            width: auto;
        }
        .st-key-construction_ai_launcher button {
            width: 3.5rem;
            height: 3.5rem;
            min-height: 3.5rem;
            border-radius: 50%;
            border: 1px solid rgba(255, 255, 255, 0.24);
            background: linear-gradient(135deg, #1B3A5B, #0E7C7B);
            box-shadow: 0 8px 24px rgba(14, 124, 123, 0.35);
            color: white;
            font-size: 1.25rem;
        }
        .st-key-construction_ai_launcher button:hover {
            border-color: rgba(255, 255, 255, 0.45);
            background: linear-gradient(135deg, #244b72, #10918f);
        }
        /* Move AI dialog closer to right side */
        div[role="dialog"] {
            margin-left: auto !important;
            margin-right: 2rem !important;
        }
        /* Compact Construction AI Copilot UI */

        /* Reduce dialog padding */
        div[role="dialog"] {
            padding-top: 0.5rem !important;
        }

        /* Reduce markdown heading sizes */
        div[role="dialog"] h2 {
            font-size: 1.2rem !important;
            margin-bottom: 0.2rem !important;
        }

        div[role="dialog"] h3 {
            font-size: 1rem !important;
            margin-bottom: 0.2rem !important;
        }

        /* Reduce vertical spacing between elements */
        div[role="dialog"] .stMarkdown {
            margin-bottom: 0.2rem !important;
        }

        /* Compact buttons */
        div[role="dialog"] button {
            min-height: 2rem !important;
            height: 2rem !important;
            padding: 0.15rem 0.5rem !important;
            font-size: 0.85rem !important;
        }

        /* Compact alert box */
        div[role="dialog"] .stAlert {
            padding: 0.35rem 0.6rem !important;
            margin-bottom: 0.3rem !important;
        }

        /* Compact divider spacing */
        div[role="dialog"] hr {
            margin: 0.4rem 0 !important;
        }
        /* AI chat internal scrolling */
        .ai-chat-container {
            max-height: 35vh;
            overflow-y: auto;
            padding-right: 0.4rem;
        }
        .ai-history {
            max-height: 380px;
            overflow-y: auto;
            padding-right: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "ai_open" not in st.session_state:
        st.session_state["ai_open"] = False


    if st.button(
        "✨",
        key="construction_ai_launcher",
        help="Open Construction AI Assistant",
    ):
        st.session_state["ai_open"] = True


    if st.session_state["ai_open"]:
        _render_assistant_dialog(_build_context())