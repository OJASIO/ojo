import streamlit as st
import os

# Page Config
st.set_page_config(page_title="Ojas Indulkar | Data Engineer", page_icon="📊", layout="wide")

# --- NAVIGATION CONTROLLER ---
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

def set_page(page_name):
    st.session_state.page = page_name

# --- SIDEBAR / TOP NAVIGATION ---
st.sidebar.title("Navigation")
if st.sidebar.button("🏠 Home"):
    set_page('Home')
if st.sidebar.button("🏢 Professional Experience"):
    set_page('Experience')
if st.sidebar.button("🎓 Education & Projects"):
    set_page('Education')

# --- IMAGE PATH LOGIC ---
current_dir = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(current_dir, "profile.PNG")

# --- PAGE: HOME ---
if st.session_state.page == 'Home':
    col1, col2 = st.columns([1, 3])
    with col1:
        if os.path.exists(img_path):
            st.image(img_path, width=220)
        else:
            st.warning("Photo not found.")
    with col2:
        st.title("Ojas Indulkar")
        st.subheader("Senior Data Engineer | M.Sc. Applied Data Science Candidate")
        st.info("5+ Years of Industry Experience in FinTech & Cloud Architecture. Available for Working Student roles in Frankfurt.")
        st.write("Click the buttons in the sidebar to explore my journey.")

# --- PAGE: PROFESSIONAL EXPERIENCE ---
elif st.session_state.page == 'Experience':
    st.header("🏢 Professional Journey")
    
    # Yubi Section
    st.subheader("Data Engineer II | Yubi, Mumbai (2024)")
    st.write("- **Lead for AWS Migration:** Managed 8 people for a private cloud migration for a major bank.")
    st.write("- **Revenue Growth:** Streamlined onboarding, increasing revenue by 40%.")
    
    # Teradata Section
    st.subheader("SME Data Engineer | Teradata India (2019-2022)")
    st.write("- **SLA Optimization:** Reduced critical job runtime by 85%.")
    st.write("- **Financial Recovery:** Saved millions in spend variances for Unilever.")
    
    if st.button("⬅️ Back to Home"):
        set_page('Home')

# --- PAGE: EDUCATION ---
elif st.session_state.page == 'Education':
    st.header("🎓 Education & Strategic Projects")
    
    st.write("**M.Sc. Applied Data Science and Analytics**")
    st.write("SRH Hochschule Heidelberg | Expected 2027")
    
    st.divider()
    st.subheader("🚀 Strategic Projects")
    st.write("- **Frankfurt Market Risk Engine:** ETL pipeline for DAX 40 volatility.")
    st.write("- **Global Spend Analyzer:** Tableau visualization for MNC procurement.")

    if st.button("⬅️ Back to Home"):
        set_page('Home')

st.divider()
st.write("Built with ❤️ in Heidelberg | © 2026 Ojas Indulkar")
