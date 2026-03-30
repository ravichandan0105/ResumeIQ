import streamlit as st
import re
from pdfminer.high_level import extract_text
import plotly.graph_objects as go
import os
import spacy

# ---------------- NLP ----------------
try:
    nlp = spacy.load("en_core_web_sm")
except:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# ---------------- CONFIG ----------------
st.set_page_config(page_title="ResumeIQ", page_icon="📄", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.card {
    padding: 18px;
    border-radius: 16px;
    background: linear-gradient(145deg, #1f2937, #111827);
    box-shadow: 0 6px 18px rgba(0,0,0,0.4);
    color: white;
}
.card-title { color: #9ca3af; font-size: 14px; }
.card-value { font-size: 20px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("<h1 style='text-align:center;'>📄 ResumeIQ</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>Analyze • Improve • Get Hired</p>", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def extract_email(text):
    match = re.findall(r"[\w\.-]+@[\w\.-]+", text)
    return match[0] if match else None

def extract_phone(text):
    match = re.findall(r"\+?\d[\d -]{8,12}\d", text)
    return match[0] if match else None

def extract_name(text):
    doc = nlp(text[:1000])
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_skills(text):
    skills_list = ["python","java","c++","machine learning","data science",
                   "html","css","javascript","react","sql","excel"]
    text = text.lower()
    return [s for s in skills_list if re.search(rf"\b{s}\b", text)]

# ---------------- UPLOAD ----------------
file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if file:
    with open(file.name, "wb") as f:
        f.write(file.read())

    text = extract_text(file.name)

    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)

    col1, col2, col3 = st.columns(3)

    col1.markdown(f"<div class='card'><div class='card-title'>Name</div><div class='card-value'>{name or 'Not Found'}</div></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'><div class='card-title'>Email</div><div class='card-value'>{email or 'Not Found'}</div></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'><div class='card-title'>Phone</div><div class='card-value'>{phone or 'Not Found'}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"<div class='card'><b>Skills:</b><br>{', '.join(skills) if skills else 'None'}</div>", unsafe_allow_html=True)

    # ---------------- FIELD ----------------
    field = "General"
    if any(s in skills for s in ["python","machine learning"]):
        field = "Data Science"
    elif any(s in skills for s in ["html","css","javascript"]):
        field = "Web Development"

    st.metric("Recommended Field", field)

    # ---------------- SCORE ----------------
    score = 0
    if "objective" in text.lower(): score += 20
    if "projects" in text.lower(): score += 20
    if "skills" in text.lower(): score += 20
    if "education" in text.lower(): score += 20
    if "experience" in text.lower(): score += 20

    st.markdown("## 🎯 Resume Score")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        gauge={'axis': {'range': [0,100]}}
    ))
    st.plotly_chart(fig, use_container_width=True)

    # ---------------- RECOMMENDED SKILLS ----------------
    if field == "Data Science":
        rec_skills = ["TensorFlow","Pandas","ML Algorithms"]
    elif field == "Web Development":
        rec_skills = ["React","Node.js","MongoDB"]
    else:
        rec_skills = []

    if rec_skills:
        st.markdown(f"<div class='card'><b>Recommended Skills</b><br>{', '.join(rec_skills)}</div>", unsafe_allow_html=True)

    # ---------------- COURSES ----------------
    from courses import ds_courses, web_courses

    st.markdown("## 🎓 Courses")

    selected = ds_courses if field=="Data Science" else web_courses

    for c, link in selected:
        st.markdown(f"<div class='card'>📘 {c}<br><a href='{link}'>Open</a></div>", unsafe_allow_html=True)

    # ---------------- SUGGESTIONS ----------------
    st.markdown("## 💡 Suggestions")

    if "projects" not in text.lower():
        st.warning("Add projects")
    if "objective" not in text.lower():
        st.warning("Add career objective")

    os.remove(file.name)

else:
    st.info("Upload a resume to start")