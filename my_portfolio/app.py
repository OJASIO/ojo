import streamlit as st
import os

# Page Config
st.set_page_config(page_title="Ojas Indulkar | Data Engineer", page_icon="📊", layout="wide")

# --- BULLETPROOF IMAGE PATH LOGIC ---
# This finds the directory where app.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Joins the directory path with your filename
img_path = os.path.join(current_dir, "profile.PNG")

# --- HEADER SECTION ---
with st.container():
    col1, col2 = st.columns([1, 3])
    with col1:
        if os.path.exists(img_path):
            st.image(img_path, width=220)
        else:
            # Fallback to prevent crash
            st.warning("Photo not found. Checking root...")
            if os.path.exists("profile.PNG"):
                st.image("profile.PNG", width=220)
            else:
                st.error("Image file missing on server.")
            
    with col2:
        [cite_start]st.title("Ojas Indulkar") [cite: 10]
        [cite_start]st.subheader("Senior Data Engineer | M.Sc. Applied Data Science Candidate") [cite: 11, 83-85]
        [cite_start]st.write("📍 Heidelberg, Germany | 📧 indulkarojas08@gmail.com") [cite: 2, 4, 9]
        [cite_start]st.write("📱 +49 015510136816") [cite: 5, 6]
        [cite_start]st.info("4+ Years of experience in ETL, Data Warehousing, and Cloud Solutions.") [cite: 11, 14]

st.divider()

# --- PROFESSIONAL EXPERIENCE ---
st.header("🏢 Professional Journey")

# Yubi Experience
with st.expander("🚀 Data Engineer II | Yubi, Mumbai", expanded=True):
    [cite_start]st.write("01/2024 – 08/2024") [cite: 19, 20]
    [cite_start]st.write("- **Leadership:** Led a team of 8 people, delegating tasks and collaborating with cross-functional teams.") [cite: 21]
    [cite_start]st.write("- **Cloud Migration:** Acted as lead for a data migration project from public AWS to private AWS cloud for large banks.") [cite: 23]
    [cite_start]st.write("- **Business Impact:** Streamlined report development, increasing revenue by 40%.") [cite: 22]

# SpanIdea Experience
with st.expander("📊 Data Consultant | SpanIdea, Mumbai"):
    [cite_start]st.write("06/2022 – 12/2023") [cite: 54, 55]
    [cite_start]st.write("- **Performance:** Reduced job runtime by 50% via query tuning.") [cite: 57]
    [cite_start]st.write("- **Automation:** Automated loan summary and MIS reports using Python.") [cite: 58]

# Teradata Experience
with st.expander("🛡️ SME Data Engineer | Teradata India"):
    [cite_start]st.write("09/2019 – 06/2022") [cite: 67, 68]
    [cite_start]st.write("- **Scale:** Managed ETL for global clients like Unilever and P&G.") [cite: 69]
    [cite_start]st.write("- **Optimization:** Reduced critical SLA job runtime by 85%.") [cite: 70]

st.divider()

# --- SKILLS ---
st.header("🛠️ Technical Arsenal")
[cite_start]st.write("**Cloud:** AWS (EMR, Redshift, Athena, Beanstalk), GCP (BigQuery, PubSub).") [cite: 28-36]
[cite_start]st.write("**Data Engineering:** ETL, Data Warehousing, Airflow, Docker, Teradata BTEQ.") [cite: 37-41, 47]

st.divider()
st.write("Built with ❤️ in Heidelberg | © 2026 Ojas Indulkar")
