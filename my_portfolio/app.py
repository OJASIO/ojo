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
    st.subheader("Data Engineer II | Yubi, Mumbai (December 2023-August 2024)")
    st.write("- Joined Yubi on permanent role and Led a team of 8 people, delegating tasks and collaborating with cross-functional teams.")
    st.write("Streamlined report development process that resulted in faster onboarding of new clients thereby resulting in an increase in revenue of the firm by 40%.")
    st.write("Acted as lead from data reporting team for a data migration project from public AWS to private AWS cloud for a largest public sector bank and major private sector Indian bank.")
    st.write("Developed business reporting dashboards on the Superset Tool which helped in critical business decisions thereby, increasing revenue by 20%")
    st.write("Reduced data quality issues by 40% % through proactive code bug rectification.")
    st.write("Automated manual-generated reports using Python, increasing team efficiency by 35%.")
    st.subheader("Data Engineer | SpanIdea, Mumbai (June 2022-December 2023)")
    st.write("Developed integration reports using Python, PostgreSQL, and Airflow. long running jobs by tuning queries resulting in 50% decrease in runtime.")
    st.write("Automated Loan summary and MIS reports through Python there by increasing the efficiency of Operations team by 60%.")
    st.write("Developed Document upload script to upload loan documents, cibil and bureau data of the borrower from AWS S3 to Bank SFTP server.")
    st.write("Automated the delivery of ad-hoc lender reports via email and SFTP, ensuring real-time loan pool synchronization.")
    st.write("Facilitated a 30% increase in bank loan disbursement rate by providing lenders with frequent, high-accuracy data updates.")
    st.write("Developed pipeline to extract data from mongoDB and load it in RDS table for report generation.")
    st.write("Developed pipeline to extract data from source tables present in Datalake, stream it through Kafka and load it in Redshift Data Warehouse target tables for loan portfolio dashboard.")
    
    # Teradata Section
    st.subheader("Data Engineer | Technical Associate| Data Engineer | Teradata India (September 2019- June 2022)")
    st.write("Progressed from Intern to SME Data Engineer, eventually leading a team of 5 members to support global clients like Unilever Plc and Procter & Gamble (P&G)")
    st.write("Optimized high CPU-consuming queries by implementing volatile tables and statistics collection, reducing the runtime of critical SLA jobs by 85%.")
    st.write("Saved 5 Million euros in spend variances for Unilever through comprehensive root cause analysis of indirect procurement, media, and logistics data.")
    st.write("Engineered automation tools in Python and Shell script to identify data duplicates and remove marketing program data, increasing overall work efficiency by up to 40%.")
    st.write("Enhanced service delivery efficiency by 50% by building automated sanity check jobs in TWS and BTEQ to validate record loading in target tables. ")
    st.write("Orchestrated large-scale ETL operations, extracting data from diverse API sources and flat files into the Enterprise Data Warehouse (EDW) using Teradata BTEQ, FastLoad and TPT.")
    st.write("Mitigated legal and financial risks by automating API status checks, preventing campaign outreach to opted-out consumers and saving thousands of dollars in potential penalty costs.")
    st.write("Managed production deployments and job scheduling using GIT version control, Unix shell scripting, and Crontab.")
    
    if st.button("⬅️ Back to Home"):
        set_page('Home')

# --- PAGE: EDUCATION ---
elif st.session_state.page == 'Education':
    st.header("🎓 Education & Strategic Projects")
    
    st.write("**M.Sc. Applied Data Science and Analytics**")
    st.write("SRH Hochschule Heidelberg | April 2025 - March 2027")

    st.write("**Bachelors in Computer Engineering**")
    st.write("Terna Engineering College | June 2015 - June 2019")
    st.write("Grade: 7.75/10")
    
    st.divider()
    st.subheader("🚀 Strategic Projects")
    st.write("- **Frankfurt Market Risk Engine:** ETL pipeline for DAX 40 volatility.")
    st.write("- **Global Spend Analyzer:** Tableau visualization for MNC procurement.")

    if st.button("⬅️ Back to Home"):
        set_page('Home')

st.divider()
st.write("Built with ❤️ in Heidelberg & Frankfurt | © 2026 Ojas Indulkar")
