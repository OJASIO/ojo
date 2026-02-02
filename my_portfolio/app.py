import streamlit as st
import os

# Page Config
st.set_page_config(page_title="Ojas Indulkar | Data Engineer", page_icon="📊", layout="wide")

# --- IMAGE PATH LOGIC ---
# Using the absolute path to ensure the cloud finds the file in the same folder
current_dir = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(current_dir, "profile.PNG")

# --- HEADER SECTION ---
with st.container():
    col1, col2 = st.columns([1, 3])
    with col1:
        if os.path.exists(img_path):
            st.image(img_path, width=220)
        else:
            st.warning("Photo (profile.PNG) not found in directory.")
            
    with col2:
        # Citations are now safely inside the strings
        [cite_start]st.title("Ojas Indulkar [cite: 10]")
        [cite_start]st.subheader("Senior Data Engineer | M.Sc. Applied Data Science Candidate [cite: 11, 83-85]")
        [cite_start]st.write("📍 Heidelberg, Germany [cite: 9] | [cite_start]📧 indulkarojas08@gmail.com [cite: 2-4]")
        [cite_start]st.write("📱 +49 015510136816 [cite: 6]")
        [cite_start]st.info("4+ Years of experience in ETL, Data Warehousing, and Cloud Solutions. [cite: 11, 14]")

st.divider()

# --- PROFESSIONAL EXPERIENCE ---
st.header("🏢 Professional Journey")

# Yubi Experience
with st.expander("🚀 Data Engineer II | Yubi, Mumbai", expanded=True):
    [cite_start]st.write("01/2024 – 08/2024 [cite: 20]")
    [cite_start]st.write("- **Leadership:** Led a team of 8 people, delegating tasks and collaborating with cross-functional teams.")
    [cite_start]st.write("- **Cloud Migration:** Acted as lead for a data migration project from public AWS to private AWS cloud for large banks.")
    [cite_start]st.write("- **Business Impact:** Streamlined report development, increasing revenue by 40%.")

# SpanIdea Experience
with st.expander("📊 Data Consultant | SpanIdea, Mumbai"):
    [cite_start]st.write("06/2022 – 12/2023 [cite: 55]")
    [cite_start]st.write("- **Performance:** Reduced job runtime by 50% via query tuning.")
    [cite_start]st.write("- **Automation:** Automated loan summary and MIS reports using Python.")
    [cite_start]st.write("- **Integration:** Developed pipelines to stream data through Kafka into Redshift.")

# Teradata Experience
with st.expander("🛡️ SME Data Engineer | Teradata India"):
    [cite_start]st.write("09/2019 – 06/2022")
    [cite_start]st.write("- **Scale:** Managed ETL for global clients like Unilever and P&G.")
    [cite_start]st.write("- **Optimization:** Reduced critical SLA job runtime by 85% using volatile tables and statistics.")
    [cite_start]st.write("- **Recovery:** Recovered millions of euros in spend variances for Unilever.")

st.divider()

# --- SKILLS ---
st.header("🛠️ Technical Arsenal")
[cite_start]st.write("**Cloud:** AWS (EMR, Redshift, Athena, Beanstalk), GCP (BigQuery, PubSub).")
[cite_start]st.write("**Data Engineering:** ETL, Data Warehousing, Airflow, Docker, Teradata BTEQ.")
[cite_start]st.write("**Languages:** Python, SQL, NumPy, Pandas.")

st.divider()
st.write("Built with ❤️ in Heidelberg | © 2026 Ojas Indulkar")
