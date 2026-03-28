import streamlit as st
import spacy
import re
from pdfminer.high_level import extract_text

# Load NLP
nlp = spacy.load("en_core_web_sm")

# Page setup
st.set_page_config(page_title="ResumeIQ", page_icon="📄")

st.title("📄 ResumeIQ")
st.write("Analyze. Improve. Get Hired.")

st.write("---")

# Upload
file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

# -------- FUNCTIONS --------

def extract_email(text):
    match = re.findall(r"[\\w\\.-]+@[\\w\\.-]+", text)
    return match[0] if match else "Not found"

def extract_phone(text):
    match = re.findall(r"\\+?\\d[\\d -]{8,12}\\d", text)
    return match[0] if match else "Not found"

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "Not found"

def extract_skills(text):
    skills_list = ["python","java","c++","machine learning","data science",
                   "html","css","javascript","react","sql","excel"]

    found = []
    text_lower = text.lower()

    for skill in skills_list:
        if skill in text_lower:
            found.append(skill)

    return list(set(found))

# -------- MAIN --------

if file:
    st.success("File uploaded successfully!")

    # Save temp file
    with open("temp.pdf", "wb") as f:
        f.write(file.read())

    # Extract text
    text = extract_text("temp.pdf")

    st.write("---")
    st.subheader("📊 Extracted Information")

    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)

    st.write("👤 Name:", name)
    st.write("📧 Email:", email)
    st.write("📱 Phone:", phone)
    st.write("💡 Skills:", skills)