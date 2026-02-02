import streamlit as st

st.set_page_config(page_title="Ojas Indulkar | Data Engineer", layout="wide")

# Header
st.title("Ojas Indulkar")
st.subheader("Senior Data Engineer | Pursuing MSc Applied Data Science Candidate at SRH Hochschule Heidelberg")

# Experience Section
with st.expander("Professional Experience"):
    st.write("**Yubi (Mumbai)** - Lead Data Engineer (2024)")
    st.write("- Managed migration for India's largest public sector bank.")
    st.write("**Teradata** - SME Data Engineer (2019-2022)")
    st.write("- Optimized SLA jobs by 85%.")

# Projects Section
st.header("Project Showcase")
col1, col2 = st.columns(2)
with col1:
    st.write("### Tableau: Frankfurt Market Analysis")
    # You can add a screenshot or a link here
with col2:
    st.write("### Data Pipeline: ESG Risk Engine")
    st.write("Tech: Python, SQL, Airflow")