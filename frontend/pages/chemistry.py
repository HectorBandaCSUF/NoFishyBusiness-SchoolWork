import streamlit as st
import base64
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.app import backend_post

st.set_page_config(page_title="Chemistry Analyzer", page_icon="🧪")
st.title("🧪 Chemistry Analyzer")
st.markdown("Describe your water test results to get a danger assessment and corrective actions.")

with st.form("chemistry_form"):
    description = st.text_area(
        "Water Parameter Description",
        placeholder="e.g., ammonia is 0.5 ppm, nitrite 0.25 ppm, pH 7.2, temperature 78F"
    )
    image_file = st.file_uploader("Upload Test Strip Image (optional)", type=["jpg", "jpeg", "png"])
    submitted = st.form_submit_button("Analyze")

if submitted:
    image_base64 = None
    if image_file is not None:
        image_bytes = image_file.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    with st.spinner("Loading..."):
        result = backend_post("/chemistry", {"description": description, "image_base64": image_base64})

    if result:
        if "error_type" in result:
            st.warning(result.get("message", "An error occurred."))
        else:
            st.subheader("Parameter Analysis")
            parameters = result.get("parameters", [])
            if parameters:
                for param in parameters:
                    status = param.get("status", "unknown")
                    color = {"safe": "🟢", "caution": "🟡", "danger": "🔴"}.get(status, "⚪")
                    st.markdown(f"{color} **{param.get('name', 'N/A')}**: {param.get('value', 'N/A')} — {status.capitalize()}")
                    if param.get("corrective_action"):
                        st.markdown(f"  → *{param['corrective_action']}*")

            st.subheader("Summary")
            st.write(result.get("summary", "N/A"))
