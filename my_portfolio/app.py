import streamlit as st

# Page Config
st.set_page_config(page_title="Ojas Indulkar | Data Engineer", page_icon="📊", layout="wide")

# Header Section
with st.container():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("profile.jpg", width=220)
    with col2:
        st.title("Ojas Indulkar [cite: 10]")
        st.subheader("Senior Data Engineer | M.Sc. Applied Data Science Candidate [cite: 11, 85]")
        st.write("📍 Heidelberg, Germany [cite: 9] | 📧 indulkarojas08@gmail.com [cite: 3, 4]")
        st.write("📱 +49 015510136816 [cite: 6]")
        st.info("4+ Years of experience in ETL, Data Warehousing, and Cloud Solutions. [cite: 11, 14]")

st.divider()

# --- PROFESSIONAL EXPERIENCE ---
st.header("🏢 Professional Journey")

# Yubi Experience
with st.expander("🚀 Data Engineer II | Yubi, Mumbai", expanded=True):
    st.write("01/2024 – 08/2024 [cite: 20]")
    st.write("- **Leadership:** Led a team of 8 people, delegating tasks and collaborating with cross-functional teams. [cite: 21]")
    st.write("- **Cloud Migration:** Acted as lead for a data migration project from public AWS to private AWS cloud for a large public sector bank. [cite: 23]")
    st.write("- **Business Impact:** Streamlined report development, increasing revenue of the firm by 40%. [cite: 22]")

# SpanIdea Experience
with st.expander("📊 Data Consultant | SpanIdea, Mumbai"):
    st.write("06/2022 – 12/2023 [cite: 55]")
    st.write("- **ETL Performance:** Reduced long-running job runtimes by 50% through query tuning. [cite: 57]")
    st.write("- **Automation:** Developed Document upload scripts from AWS S3 to Bank SFTP server. [cite: 59]")
    st.write("- **Streaming:** Developed pipelines to stream data through Kafka into Redshift Data Warehouse. [cite: 63]")

# Teradata Experience
with st.expander("🛡️ SME Data Engineer | Teradata India"):
    st.write("09/2019 – 06/2022 [cite: 68]")
    st.write("- **Optimization:** Reduced runtime of critical SLA jobs by 85% by implementing volatile tables and statistics. [cite: 70]")
    st.write("- **Financial Recovery:** Recovered millions of euros in spend variances for Unilever through root cause analysis. [cite: 71]")
    st.write("- **Automation:** Engineered tools in Python and Shell to increase work efficiency by up to 40%. [cite: 72]")

st.divider()

# --- SKILLS ---
st.header("🛠️ Technical Arsenal")
st.write("**Cloud:** AWS (EMR, Redshift, Athena, Beanstalk), GCP (BigQuery, PubSub). [cite: 28-36]")
st.write("**Data Engineering:** ETL, Data Warehousing, Airflow, Docker, Teradata BTEQ. [cite: 37-41, 47]")
st.write("**Languages & DB:** Python, SQL, PostgreSQL, Redis, MongoDB. [cite: 39, 45, 46, 62]")

st.divider()

# --- EDUCATION ---
st.header("🎓 Education")
st.write("**Master's Degree in Applied Data Science and Analytics** [cite: 83, 85]")
st.write("SRH Hochschule Heidelberg | Expected 2027 (Currently 2nd Semester) [cite: 84, 86, 87]")
st.write("**Bachelor's Degree in Computer Engineering** [cite: 78, 80]")
st.write("Terna Engineering College | Grade: 7.75/10 [cite: 79, 81]")

st.divider()
st.write("Built with ❤️ in Heidelberg | © 2026 Ojas Indulkar")