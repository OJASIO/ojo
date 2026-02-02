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
        st.title("Ojas Indulkar")
        st.subheader("Senior Data Engineer | M.Sc. Applied Data Science Candidate")
        st.write("📍 Heidelberg, Germany|📧 indulkarojas08@gmail.com")
        st.write("📱 +49 015510136816")
        st.info("4+ Years of experience in ETL, Data Warehousing, and Cloud Solutions.")

st.divider()

# --- PROFESSIONAL EXPERIENCE ---
st.header("🏢 Professional Journey")

# Yubi Experience
with st.expander("🚀 Data Engineer II | Yubi, Mumbai", expanded=True):
    st.write("01/2024 – 08/2024 [cite: 20]")
    st.write("- **Leadership:** Led a team of 8 people, delegating tasks and collaborating with cross-functional teams.")
    st.write("- **Cloud Migration:** Acted as lead for a data migration project from public AWS to private AWS cloud for large banks.")
    st.write("- **Business Impact:** Streamlined report development, increasing revenue by 40%.")

# SpanIdea Experience
with st.expander("📊 Data Consultant | SpanIdea, Mumbai"):
    st.write("06/2022 – 12/2023 [cite: 55]")
    st.write("- **Performance:** Reduced job runtime by 50% via query tuning.")
    st.write("- **Automation:** Automated loan summary and MIS reports using Python.")
    st.write("- **Integration:** Developed pipelines to stream data through Kafka into Redshift.")

# Teradata Experience
with st.expander("🛡️ SME Data Engineer | Teradata India"):
    st.write("09/2019 – 06/2022")
    st.write("- **Scale:** Managed ETL for global clients like Unilever and P&G.")
    st.write("- **Optimization:** Reduced critical SLA job runtime by 85% using volatile tables and statistics.")
    st.write("- **Recovery:** Recovered millions of euros in spend variances for Unilever.")

st.divider()

# --- SKILLS ---
st.header("🛠️ Technical Arsenal")
st.write("**Cloud:** AWS (EMR, Redshift, Athena, Beanstalk), GCP (BigQuery, PubSub).")
st.write("**Data Engineering:** ETL, Data Warehousing, Airflow, Docker, Teradata BTEQ.")
st.write("**Languages:** Python, SQL, NumPy, Pandas.")

st.divider()
st.write("Built with ❤️ in Heidelberg | © 2026 Ojas Indulkar")
