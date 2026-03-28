import streamlit as st
import spacy
import re
from pdfminer.high_level import extract_text
import pymysql
import datetime
import pandas as pd
import random
import plotly.express as px

# ---------------- IMPORT COURSES ----------------
from courses import ds_courses, web_courses, android_courses, resume_videos, interview_videos

# ---------------- DATABASE ----------------
connection = pymysql.connect(
    host="localhost",
    user="root",
    password=""
)

cursor = connection.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS resumeiq_db")
connection.select_db("resumeiq_db")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    score INT,
    field VARCHAR(50),
    level VARCHAR(50),
    timestamp VARCHAR(50)
)
""")

# ---------------- NLP ----------------
nlp = spacy.load("en_core_web_sm")

# ---------------- UI ----------------
st.set_page_config(page_title="ResumeIQ", page_icon="📄")

st.title("📄 ResumeIQ")
st.write("Analyze. Improve. Get Hired.")
st.write("---")

# Upload
file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

# ---------------- FUNCTIONS ----------------

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

# ---------------- MAIN ----------------

if file:
    st.success("File uploaded successfully!")

    with open("temp.pdf", "wb") as f:
        f.write(file.read())

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

    # ---------------- ANALYSIS ----------------
    st.write("---")
    st.subheader("📊 Resume Analysis")

    pages = text.count("\n") // 50 + 1

    if pages == 1:
        level = "Fresher"
    elif pages == 2:
        level = "Intermediate"
    else:
        level = "Experienced"

    st.write(f"👨‍💻 Candidate Level: {level}")

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

    # ---------------- SCORE ----------------
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

    # ---------------- RECOMMENDATIONS ----------------
    st.write("---")
    st.subheader("💡 Recommendations")

    if field == "Data Science":
        recommended_skills = ["pandas", "numpy", "machine learning", "deep learning", "matplotlib"]
        selected_courses = ds_courses

    elif field == "Web Development":
        recommended_skills = ["node.js", "express", "mongodb", "tailwind", "next.js"]
        selected_courses = web_courses

    elif field == "Android Development":
        recommended_skills = ["firebase", "api integration", "ui/ux", "jetpack compose"]
        selected_courses = android_courses

    else:
        recommended_skills = ["communication", "problem solving", "git", "projects"]
        selected_courses = []

    st.write("📌 Recommended Skills:")
    st.write(recommended_skills)

    st.subheader("🎓 Recommended Courses")

    for course, link in selected_courses[:4]:
        st.write(f"• [{course}]({link})")

    # ---------------- VIDEOS ----------------
    st.write("---")
    st.subheader("🎥 Resume Tips")

    st.video(random.choice(resume_videos))

    st.subheader("🎤 Interview Tips")
    st.video(random.choice(interview_videos))

    # ---------------- DATABASE SAVE ----------------
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO users (name,email,score,field,level,timestamp) VALUES (%s,%s,%s,%s,%s,%s)",
        (name, email, score, field, level, ts)
    )

    connection.commit()

# ---------------- ADMIN DASHBOARD ----------------

st.write("---")
st.subheader("🔐 Admin Login")

admin_user = st.text_input("Username")
admin_pass = st.text_input("Password", type="password")

if st.button("Login"):
    if admin_user == "admin" and admin_pass == "resumeiq":
        st.success("Welcome Admin 👨‍💻")

        cursor.execute("SELECT * FROM users")
        data = cursor.fetchall()

        df = pd.DataFrame(data, columns=[
            "ID","Name","Email","Score","Field","Level","Time"
        ])

        st.subheader("📊 User Data")
        st.dataframe(df)

        # -------- CHARTS --------
        st.subheader("📊 Field Distribution")
        field_counts = df["Field"].value_counts()
        fig = px.pie(values=field_counts.values, names=field_counts.index)
        st.plotly_chart(fig)

        st.subheader("📊 User Level Distribution")
        level_counts = df["Level"].value_counts()
        fig2 = px.pie(values=level_counts.values, names=level_counts.index)
        st.plotly_chart(fig2)

    else:
        st.error("Invalid Credentials")