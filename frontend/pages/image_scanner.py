import streamlit as st
import requests
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.app import BACKEND_URL

st.set_page_config(page_title="Image Scanner", page_icon="📷")
st.title("📷 Image Scanner")
st.markdown("Upload a photo of a fish or plant to identify the species and assess its health.")

uploaded_file = st.file_uploader("Upload Image (JPEG or PNG, max 10 MB)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    
    if st.button("Scan Image"):
        with st.spinner("Loading..."):
            try:
                file_bytes = uploaded_file.getvalue()
                files = {"file": (uploaded_file.name, file_bytes, uploaded_file.type)}
                resp = requests.post(f"{BACKEND_URL}/image-scan", files=files, timeout=60)
                if resp.ok:
                    result = resp.json()
                    st.subheader("Identification Results")
                    species = result.get("species_name")
                    confidence = result.get("confidence", "inconclusive")
                    if species:
                        st.markdown(f"**Species:** {species}")
                        st.markdown(f"**Confidence:** {confidence.capitalize()}")
                    else:
                        st.markdown("**Species:** Could not be identified (inconclusive)")
                    
                    st.subheader("Care Summary")
                    st.write(result.get("care_summary", "N/A"))
                    
                    st.subheader("Health Assessment")
                    health = result.get("health_assessment", {})
                    st.markdown(f"**Status:** {health.get('status', 'N/A')}")
                    issues = health.get("issues_detected")
                    if issues:
                        st.markdown("**Issues Detected:**")
                        for issue in issues:
                            st.markdown(f"- {issue}")
                    else:
                        st.markdown("**Issues Detected:** None")
                else:
                    try:
                        err = resp.json()
                        st.error(f"Error: {err.get('message', 'Unknown error')}")
                    except Exception:
                        st.error("An unexpected error occurred. Please try again.")
            except requests.RequestException:
                st.error("Could not reach the backend. Please ensure it is running.")
            except Exception:
                st.error("The result could not be displayed. Please retry.")
