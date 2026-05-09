import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"


def handle_backend_response(resp):
    """Parse and display backend response or error.

    Returns the parsed JSON dict on success, or None on HTTP error.
    Displays st.error with the backend's message field when available,
    or a generic fallback message when the response body cannot be parsed.
    """
    if resp.ok:
        return resp.json()
    else:
        try:
            err = resp.json()
            st.error(f"Error: {err['message']}")
        except Exception:
            st.error("An unexpected error occurred. Please try again.")
        return None


def backend_post(endpoint, payload):
    """POST to backend with shared error handling.

    Returns the parsed JSON dict on success, or None on any error.
    Displays an appropriate st.error message for each failure mode:
      - HTTP error: shows the backend's message field (or fallback)
      - requests.RequestException: "Could not reach the backend"
      - Any other exception: "The result could not be displayed"
    """
    try:
        resp = requests.post(
            f"{BACKEND_URL}{endpoint}", json=payload, timeout=30
        )
        return handle_backend_response(resp)
    except requests.RequestException:
        st.error("Could not reach the backend. Please ensure it is running.")
        return None
    except Exception:
        st.error("The result could not be displayed. Please retry.")
        return None


# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(page_title="NoFishyBusiness", page_icon="🐟", layout="wide")

# ── Sidebar navigation ────────────────────────────────────────────────────────
st.sidebar.title("🐟 NoFishyBusiness")
st.sidebar.markdown("---")
st.sidebar.page_link("pages/volume.py", label="📐 Volume Calculator")
st.sidebar.page_link("pages/species.py", label="🐠 Species Tool")
st.sidebar.page_link("pages/maintenance.py", label="🔧 Maintenance Guide")
st.sidebar.page_link("pages/setup.py", label="🌱 Setup Guide")
st.sidebar.page_link("pages/chemistry.py", label="🧪 Chemistry Analyzer")
st.sidebar.page_link("pages/image_scanner.py", label="📷 Image Scanner")
st.sidebar.page_link("pages/assistant.py", label="🤖 AI Assistant")

# ── Home page content ─────────────────────────────────────────────────────────
st.title("Welcome to NoFishyBusiness 🐟")
st.markdown("""
Your AI-powered aquarium companion. Select a tool from the sidebar to get started.

**Available Tools:**
- **Volume Calculator** — Compute tank water volume and weight
- **Species Tool** — Look up fish care sheets
- **Maintenance Guide** — Get nitrogen cycle and maintenance advice
- **Setup Guide** — Get beginner-friendly tank setup recommendations
- **Chemistry Analyzer** — Analyze water test results
- **Image Scanner** — Identify fish and plants from photos
- **AI Assistant** — Ask free-form aquarium questions
""")
