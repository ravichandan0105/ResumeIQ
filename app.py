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
    skills_list = [
        "python","java","c++","machine learning","data science",
        "html","css","javascript","react","sql","excel"
    ]

    found = []
    text_lower = text.lower()

    for skill in skills_list:
        if skill in text_lower:
            found.append(skill)

    return list(set(found))

# -------- MAIN --------

if file:
    st.success("File uploaded successfully!")

    # Save file
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

    # -------- ANALYSIS --------
    st.write("---")
    st.subheader("📊 Resume Analysis")

    # Level
    pages = text.count("\n") // 50 + 1

    if pages == 1:
        level = "Fresher"
    elif pages == 2:
        level = "Intermediate"
    else:
        level = "Experienced"

    st.write(f"👨‍💻 Candidate Level: {level}")

    # Field
    field = "General"

    ds_keywords = ["python", "machine learning", "data science"]
    web_keywords = ["html", "css", "javascript", "react"]
    android_keywords = ["android", "kotlin", "flutter"]

    skills_lower = [s.lower() for s in skills]

    if any(skill in skills_lower for skill in ds_keywords):
        field = "Data Science"
    elif any(skill in skills_lower for skill in web_keywords):
        field = "Web Development"
    elif any(skill in skills_lower for skill in android_keywords):
        field = "Android Development"

    st.info(f"💼 Recommended Field: {field}")

    # Score
    score = 0

    if name != "Not found":
        score += 20
    if email != "Not found":
        score += 20
    if phone != "Not found":
        score += 10
    if skills:
        score += 30
    if len(text) > 1000:
        score += 20

    score = min(score, 100)

    st.subheader("🎯 Resume Score")
    st.progress(score)
    st.success(f"Your Resume Score: {score}/100")