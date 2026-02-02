import streamlit as st
import pandas as pd

# Page Config
st.set_page_config(page_title="Ojas Indulkar | Data Engineer", page_icon="📊", layout="wide")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #004466;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER SECTION ---
with st.container():
    col1, col2 = st.columns([1, 3])
    with col1:
        # Make sure 'profile.jpg' is in your GitHub repo folder
        st.image("profile.jpg", width=220)
    with col2:
        st.title("Ojas Indulkar")
        st.subheader("Senior Data Engineer | M.Sc. Applied Data Science Candidate")
        st.write("📍 Heidelberg, Germany | 📧 [indulkarojas08@gmail.com](mailto:indulkarojas08@gmail.com)")
        st.write("🔗 [LinkedIn](https://linkedin.com/in/indulkarojas08) | 💻 [GitHub](https://github.com/indulkarojas08)")
        st.info("5+ Years of Industry Experience in FinTech & Cloud Architecture (AWS/GCP). Available for Working Student roles (20h/week).")

st.divider()

# --- PROFESSIONAL EXPERIENCE ---
st.header("🏢 Professional Journey")

# Yubi Experience
with st.expander("🚀 Data Engineer II | Yubi, Mumbai", expanded=True):
    [cite_start]st.write("01/2024 – 08/2024 [cite: 20]")
    st.write("""
    - [cite_start]**Team Leadership:** Led a cross-functional team of 8 members, delegating technical tasks and ensuring project delivery[cite: 21].
    - [cite_start]**Cloud Migration:** Acted as technical lead for a massive data migration from public AWS to private AWS cloud for India's largest public sector bank[cite: 23].
    - [cite_start]**Revenue Impact:** Streamlined report development, increasing firm revenue by 40% through faster client onboarding[cite: 22].
    - [cite_start]**Optimization:** Developed Python automation scripts and Superset dashboards, reducing data quality issues by 40%[cite: 24, 25, 26].
    """)

# SpanIdea Experience
with st.expander("📊 Data Consultant | SpanIdea, Mumbai"):
    [cite_start]st.write("06/2022 – 12/2023 [cite: 55]")
    st.write("""
    - [cite_start]**ETL Pipelines:** Built robust pipelines using Python, PostgreSQL, and Airflow, achieving a 50% decrease in runtime for long-running jobs[cite: 56, 57].
    - [cite_start]**Automation:** Developed document upload scripts for AWS S3 to Bank SFTP servers, facilitating a 30% increase in loan disbursement rates[cite: 59, 61].
    - [cite_start]**Data Streaming:** Engineered pipelines to stream data from Data Lakes through Kafka into Redshift target tables[cite: 63].
    """)

# Teradata Experience
with st.expander("🛡️ SME Data Engineer | Teradata India"):
    [cite_start]st.write("09/2019 – 06/2022 [cite: 68]")
    st.write("""
    - [cite_start]**Global Scale:** Supported Fortune 500 clients like Unilever and P&G[cite: 69].
    - [cite_start]**Performance Tuning:** Optimized high-CPU queries using volatile tables and statistics, reducing SLA job runtime by 85%[cite: 70].
    - [cite_start]**Financial Impact:** Recovered millions of euros in spend variances for Unilever through root cause analysis of procurement data[cite: 71].
    - [cite_start]**Tech:** Teradata BTEQ, FastLoad, TPT, Unix Shell Scripting[cite: 74, 76].
    """)

st.divider()

# --- SKILLS & TOOLS ---
st.header("🛠️ Technical Arsenal")
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.write("**Cloud & Infra**")
    [cite_start]st.write("- AWS (EMR, Redshift, Athena, S3) [cite: 31, 32, 33]")
    [cite_start]st.write("- GCP (BigQuery, PubSub, Cloud Functions) [cite: 34, 35, 36]")
    [cite_start]st.write("- Docker & Airflow [cite: 40, 41]")

with col_b:
    st.write("**Data Engineering**")
    [cite_start]st.write("- ETL Frameworks & Data Warehousing [cite: 37, 38]")
    [cite_start]st.write("- Teradata SQL & BTEQ [cite: 47]")
    [cite_start]st.write("- Kafka & Redis [cite: 45, 63]")

with col_c:
    st.write("**Programming & Viz**")
    [cite_start]st.write("- Python (Pandas, NumPy, Scikit-learn) [cite: 29, 30, 42]")
    [cite_start]st.write("- SQL (PostgreSQL, SQLAlchemy) [cite: 39, 46, 49]")
    [cite_start]st.write("- Tableau & Superset [cite: 24, 44]")

st.divider()

# --- EDUCATION ---
st.header("🎓 Education")
col_ed1, col_ed2 = st.columns(2)

with col_ed1:
    [cite_start]st.write("**M.Sc. Applied Data Science and Analytics** [cite: 85]")
    [cite_start]st.write("SRH Hochschule Heidelberg, Germany [cite: 84]")
    [cite_start]st.write("Graduation: 2027 (Currently 2nd Semester) [cite: 86, 87]")

with col_ed2:
    [cite_start]st.write("**B.E. in Computer Engineering** [cite: 78, 80]")
    [cite_start]st.write("Terna Engineering College, Mumbai [cite: 79]")
    [cite_start]st.write("Grade: 7.75/10 [cite: 81]")

st.divider()

# --- PORTFOLIO PROJECTS ---
st.header("🚀 Strategic Projects")
p_col1, p_col2 = st.columns(2)

with p_col1:
    st.subheader("Frankfurt Market Risk Engine")
    st.write("End-to-end ETL pipeline analyzing DAX 40 volatility. Built specifically to demonstrate German financial market understanding.")
    st.write("`Python` `Airflow` `PostgreSQL` `Docker`")

with p_col2:
    st.subheader("Global Spend Analyzer (Tableau)")
    [cite_start]st.write("Advanced visualization project mapping procurement variances for global MNCs, reflecting my work with Unilever[cite: 71].")
    st.write("`Tableau` `SQL` `Data Storytelling`")

# Footer
st.markdown("---")
st.write("Built by Ojas Indulkar in Heidelberg | © 2026 Ojas Indulkar")
st.write("Ich Komme aus Indien und wohne ich in Heidelberg")