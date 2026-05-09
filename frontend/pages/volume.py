# frontend/pages/volume.py
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.app import backend_post

st.set_page_config(page_title="Volume Calculator", page_icon="📐")
st.title("📐 Volume Calculator")
st.markdown("Enter your tank dimensions to calculate water volume and weight.")

with st.form("volume_form"):
    length = st.number_input("Length (inches)", min_value=0.01, value=24.0, step=0.5)
    width = st.number_input("Width (inches)", min_value=0.01, value=12.0, step=0.5)
    depth = st.number_input("Water Depth (inches)", min_value=0.01, value=12.0, step=0.5)
    submitted = st.form_submit_button("Calculate")

if submitted:
    with st.spinner("Loading..."):
        result = backend_post("/volume", {"length": length, "width": width, "depth": depth})
    if result:
        st.success("Calculation complete!")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Volume", f"{result['volume_gallons']} gallons")
        with col2:
            st.metric("Weight", f"{result['weight_pounds']} pounds")
