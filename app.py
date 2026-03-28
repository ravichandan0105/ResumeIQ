import streamlit as st

# Page setup
st.set_page_config(page_title="ResumeIQ", page_icon="📄")

# Simple UI
st.title("📄 ResumeIQ")
st.write("Analyze. Improve. Get Hired.")

st.write("---")

# Upload
file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if file:
    st.success("File uploaded successfully!")
    st.write("File name:", file.name)