"""Small shared translation layer for the English/Hindi interface."""
from __future__ import annotations

import streamlit as st

_HI = {
    "Dashboard": "डैशबोर्ड", "Projects": "परियोजनाएँ", "Project Portfolio": "परियोजना पोर्टफोलियो",
    "AI Tool Center": "एआई टूल सेंटर", "Analytics": "विश्लेषण", "Settings": "सेटिंग्स",
    "Workspace": "कार्यस्थान", "Appearance": "दिखावट", "Theme": "थीम", "Language": "भाषा",
    "English": "अंग्रेज़ी", "Hindi": "हिंदी", "Notifications": "सूचनाएँ",
    "No notifications": "कोई सूचना नहीं", "Mark all as read": "सभी को पढ़ा हुआ चिह्नित करें",
    "Go to Projects": "परियोजनाओं पर जाएँ", "No project added yet. Go to the Projects tab to add your first project.": "अभी कोई परियोजना नहीं जोड़ी गई है। अपनी पहली परियोजना जोड़ने के लिए परियोजनाएँ टैब पर जाएँ।",
    "Project Manager Alerts": "परियोजना प्रबंधक अलर्ट", "Enable notifications": "सूचनाएँ सक्षम करें",
    "Daily project digest": "दैनिक परियोजना सारांश", "Safety incident alerts": "सुरक्षा घटना अलर्ट",
    "Email notifications": "ईमेल सूचनाएँ", "Save email settings": "ईमेल सेटिंग्स सहेजें",
    "Send test email": "परीक्षण ईमेल भेजें", "Email delivery": "ईमेल डिलीवरी",
    "Recipient email": "प्राप्तकर्ता ईमेल", "Sender email": "भेजने वाला ईमेल",
}


def tr(text: str) -> str:
    """Return Hindi text when the signed-in user selected Hindi."""
    if st.session_state.get("language", "English") == "Hindi":
        return _HI.get(text, text)
    return text