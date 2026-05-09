import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.app import backend_post

st.set_page_config(page_title="Maintenance Guide", page_icon="🔧")
st.title("🔧 Maintenance Guide")
st.markdown("Get a personalized maintenance schedule for your aquarium.")

with st.form("maintenance_form"):
    tank_gallons = st.number_input("Tank Size (gallons)", min_value=1.0, value=20.0, step=1.0)
    fish_count = st.number_input("Number of Fish", min_value=0, value=5, step=1)
    fish_species_input = st.text_area("Fish Species (one per line)", placeholder="Guppy\nNeon Tetra\nCorydoras")
    submitted = st.form_submit_button("Get Guide")

if submitted:
    fish_species = [s.strip() for s in fish_species_input.strip().split("\n") if s.strip()]
    with st.spinner("Loading..."):
        result = backend_post("/maintenance", {
            "tank_gallons": tank_gallons,
            "fish_count": int(fish_count),
            "fish_species": fish_species
        })
    if result:
        if "message" in result and len(result) == 1:
            st.info(result["message"])
        else:
            st.subheader("Nitrogen Cycle")
            st.write(result.get("nitrogen_cycle", "N/A"))

            st.subheader("Feeding Schedule")
            feeding = result.get("feeding", {})
            st.markdown(f"**Quantity:** {feeding.get('quantity', 'N/A')}")
            st.markdown(f"**Frequency:** {feeding.get('frequency', 'N/A')}")

            st.subheader("Weekly Tasks")
            for task in result.get("weekly_tasks", []):
                st.markdown(f"- {task}")

            st.subheader("Monthly Tasks")
            for task in result.get("monthly_tasks", []):
                st.markdown(f"- {task}")
