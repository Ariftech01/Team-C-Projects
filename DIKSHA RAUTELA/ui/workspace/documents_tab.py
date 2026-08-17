"""Workspace Documents tab - construction document upload and analysis."""
from __future__ import annotations

from pathlib import Path
import re
import zipfile
from io import BytesIO

import pandas as pd
import streamlit as st

from config.settings import UPLOADS_DIR
from models.domain import Document, Project
from repository import get_repository
from services import ai_chat
from ui.components import alert, section_header
from utils.formatting import fmt_datetime


_ALLOWED_EXTENSIONS = ["pdf", "docx", "txt", "png", "jpg", "dwg", "xlsx"]
_CONSTRUCTION_KEYWORDS = (
    "construction", "project", "drawing", "plan", "boq", "bill of quantities",
    "quantity", "estimate", "schedule", "programme", "gantt", "contract", "tender",
    "site", "structural", "architectural", "civil", "mep", "electrical", "plumbing",
    "hvac", "geotechnical", "safety", "inspection", "permit", "rfi", "submittal",
    "material", "concrete", "steel", "rebar", "foundation", "procurement", "quality",
    "work method", "workforce", "progress", "survey",
)


def _extract_upload_text(filename: str, content: bytes) -> str:
    """Read lightweight searchable text without delaying the upload workflow."""
    suffix = Path(filename).suffix.casefold()
    if suffix == ".docx":
        try:
            with zipfile.ZipFile(BytesIO(content)) as archive:
                xml = archive.read("word/document.xml").decode("utf-8", errors="ignore")
                return re.sub(r"<[^>]+>", " ", xml)
        except (KeyError, OSError, zipfile.BadZipFile):
            return ""
    if suffix == ".txt":
        return content[:100_000].decode("utf-8", errors="ignore")
    # PDF and spreadsheet metadata/text may be stored in the binary payload. This
    # fast scan supplements filename validation without adding parsing dependencies.
    return content[:100_000].decode("latin-1", errors="ignore")


def _classify_document(filename: str, content: bytes) -> tuple[bool, str, str]:
    """Accept only construction-relevant files and assign a useful document type."""
    suffix = Path(filename).suffix.casefold()
    searchable_text = f"{filename} {_extract_upload_text(filename, content)}".casefold()

    if suffix == ".dwg":
        return True, "Drawings", "CAD drawing accepted as a construction document."
    if not any(keyword in searchable_text for keyword in _CONSTRUCTION_KEYWORDS):
        return (
            False,
            "",
            "This file does not appear to be construction-related. Upload documents such as drawings, BOQs, schedules, estimates, site reports, permits, contracts, safety records, or technical specifications.",
        )

    category_rules = (
        (("boq", "bill of quantities", "quantity", "estimate"), "BOQ / Estimation"),
        (("drawing", "plan", "architectural", "structural", "mep"), "Drawings"),
        (("schedule", "programme", "gantt", "progress"), "Schedule / Progress"),
        (("safety", "inspection", "quality"), "Safety / Quality"),
        (("permit", "contract", "tender", "procurement"), "Commercial / Compliance"),
        (("geotechnical", "foundation", "concrete", "steel", "civil"), "Engineering"),
    )
    for keywords, category in category_rules:
        if any(keyword in searchable_text for keyword in keywords):
            return True, category, f"Construction document accepted and classified as {category}."
    return True, "Construction", "Construction-related document accepted."


def _stored_file_path(project: Project, document: Document) -> Path:
    """Build the exact managed upload path and prevent filename path traversal."""
    return UPLOADS_DIR / f"{project.id}_{Path(document.name).name}"


def _render_upload_form(project: Project) -> None:
    section_header("Upload Construction Document", "Only construction-related files are accepted.")
    with st.form("construction_document_upload", clear_on_submit=True, border=True):
        uploaded = st.file_uploader(
            "Choose a construction document",
            type=_ALLOWED_EXTENSIONS,
            help="PDF, DOCX, TXT, image, DWG, or XLSX files up to 25 MB.",
        )
        submitted = st.form_submit_button("Validate and upload", type="primary")

    if not submitted:
        return
    if uploaded is None:
        st.warning("Choose a construction document before uploading.")
        return
    if uploaded.size > 25 * 1024 * 1024:
        st.error("This file exceeds the 25 MB upload limit. Upload a smaller construction document.")
        return

    content = uploaded.getvalue()
    accepted, category, message = _classify_document(uploaded.name, content)
    if not accepted:
        st.warning(message)
        return

    safe_name = Path(uploaded.name).name
    if any(document.name == safe_name for document in project.documents):
        st.info(f"{safe_name} is already in this project's upload history.")
        return

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = UPLOADS_DIR / f"{project.id}_{safe_name}"
    try:
        filepath.write_bytes(content)
        project.documents.insert(
            0,
            Document(
                name=safe_name,
                category=category,
                file_type=uploaded.type or Path(safe_name).suffix.lstrip("."),
                size_bytes=uploaded.size,
                summary="",
                status="Uploaded",
            ),
        )
        get_repository().save_project(project)
    except OSError:
        st.error("The document could not be saved. Please try again.")
        return

    st.success(message)
    st.rerun()


def _render_upload_history(project: Project) -> None:
    section_header("Upload History")
    history = sorted(project.documents, key=lambda document: document.uploaded_at, reverse=True)
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Name": document.name,
                    "Category": document.category,
                    "Type": document.file_type,
                    "Size": f"{document.size_bytes / 1024:.0f} KB",
                    "Uploaded": fmt_datetime(document.uploaded_at),
                    "Status": document.status,
                }
                for document in history
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )


def _delete_document(project: Project, document: Document) -> None:
    """Remove the managed file and its project record together."""
    filepath = _stored_file_path(project, document)
    try:
        if filepath.exists():
            filepath.unlink()
        project.documents = [item for item in project.documents if item.id != document.id]
        get_repository().save_project(project)
    except OSError:
        st.error(f"{document.name} could not be deleted. Please try again.")
        return
    st.success(f"Deleted {document.name}.")
    st.rerun()


def _render_document_actions(project: Project) -> None:
    section_header("Construction Document Analysis")
    for document in project.documents:
        with st.container(border=True):
            st.write(f"**{document.name}**")
            st.caption(f"{document.category} | {document.file_type} | {fmt_datetime(document.uploaded_at)}")
            if document.summary:
                st.info(document.summary)
            else:
                st.caption("No AI summary yet.")

            summary_col, delete_col = st.columns(2)
            with summary_col:
                if st.button("Summarize", key=f"sum_{document.id}", use_container_width=True):
                    with st.spinner("Analyzing construction document..."):
                        document.summary = ai_chat(
                            f"Summarize this construction document: {document.name}. Category: {document.category}.",
                            context={"page": "Documents", "project": project},
                        )
                    document.status = "Summarized"
                    get_repository().save_project(project)
                    st.rerun()
            with delete_col:
                if st.button("Delete", key=f"delete_{document.id}", use_container_width=True):
                    _delete_document(project, document)


def render(project: Project) -> None:
    _render_upload_form(project)

    if not project.documents:
        alert("No construction documents uploaded yet.", "info")
        return

    _render_upload_history(project)
    _render_document_actions(project)
