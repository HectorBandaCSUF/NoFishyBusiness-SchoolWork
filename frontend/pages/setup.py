# frontend/pages/setup.py
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.app import backend_post

st.set_page_config(page_title="Setup Guide", page_icon="🌱")
st.title("🌱 Setup Guide")
st.markdown("Get personalized recommendations for setting up your new aquarium.")

with st.form("setup_form"):
    tank_gallons = st.number_input("Tank Size (gallons)", min_value=1.0, max_value=500.0, value=20.0, step=1.0)
    experience_level = st.selectbox("Experience Level", ["beginner", "intermediate", "advanced"])
    submitted = st.form_submit_button("Get Recommendations")

if submitted:
    with st.spinner("Loading..."):
        result = backend_post("/setup", {"tank_gallons": tank_gallons, "experience_level": experience_level})
    if result:
        if "message" in result and len(result) == 1:
            st.info(result["message"])
        else:
            st.subheader("Fish Recommendations")
            for fish in result.get("fish_recommendations", []):
                st.markdown(f"- **{fish['name']}** — Difficulty: {fish['difficulty']}, Min tank: {fish['min_tank_gallons']} gal")

            st.subheader("Plant Recommendations")
            for plant in result.get("plant_recommendations", []):
                st.markdown(f"- **{plant['name']}** — Difficulty: {plant['difficulty']}")

            st.subheader("Aquascaping Idea")
            aq = result.get("aquascaping_idea", {})
            st.markdown(f"**Substrate:** {aq.get('substrate', 'N/A')}")
            st.markdown(f"**Hardscape:** {aq.get('hardscape', 'N/A')}")
            st.markdown("**Plant Zones:**")
            for zone in aq.get("plant_zones", []):
                st.markdown(f"  - {zone}")
