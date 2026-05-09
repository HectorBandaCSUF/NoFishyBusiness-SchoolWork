# frontend/pages/species.py
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.app import backend_post

st.set_page_config(page_title="Species Tool", page_icon="🐠")
st.title("🐠 Species Tool")
st.markdown("Look up care information for any freshwater aquarium fish.")

with st.form("species_form"):
    species_name = st.text_input("Fish Species Name", placeholder="e.g., Guppy, Betta, Neon Tetra")
    submitted = st.form_submit_button("Look Up")

if submitted and species_name:
    with st.spinner("Loading..."):
        result = backend_post("/species", {"species_name": species_name})
    if result:
        st.subheader(f"Care Sheet: {result.get('species_name', species_name)}")
        st.markdown(f"**Behavior:** {result.get('behavior', 'N/A')}")
        mates = result.get('compatible_tank_mates', [])
        st.markdown(f"**Compatible Tank Mates:** {', '.join(mates) if mates else 'N/A'}")
        temp = result.get('temperature_f', {})
        st.markdown(f"**Temperature:** {temp.get('min', 'N/A')}–{temp.get('max', 'N/A')} °F")
        ph = result.get('ph', {})
        st.markdown(f"**pH:** {ph.get('min', 'N/A')}–{ph.get('max', 'N/A')}")
        hardness = result.get('hardness_dgh', {})
        st.markdown(f"**Hardness:** {hardness.get('min', 'N/A')}–{hardness.get('max', 'N/A')} dGH")
        st.markdown(f"**Minimum Tank Size:** {result.get('min_tank_gallons', 'N/A')} gallons")
        st.markdown(f"**Difficulty:** {result.get('difficulty', 'N/A').capitalize()}")
        st.markdown(f"**Maintenance Notes:** {result.get('maintenance_notes', 'N/A')}")
