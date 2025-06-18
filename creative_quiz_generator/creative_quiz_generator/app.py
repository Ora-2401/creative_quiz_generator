import streamlit as st
import json
import os
from datetime import datetime
from utils.api_handler import generate_quiz
from utils.validation import validate_inputs

# Ensure required directories exist
os.makedirs("outputs/generated_text", exist_ok=True)
os.makedirs("logs", exist_ok=True)

st.set_page_config(page_title="🎓 AI Quiz Generator", layout="centered")
st.title("📚 AI Quiz Generator")

def load_quiz_prompts():
    try:
        with open("prompts/quiz_prompts.json", "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading quiz prompts: {e}")
        return {}

quiz_prompts = load_quiz_prompts()
if not quiz_prompts:
    st.stop()

grade = st.selectbox("🎓 Select Grade Level", ["Grade 4", "Grade 5", "Grade 6", "Grade 7", "Grade 8"])
subject = st.selectbox("📘 Choose Subject", list(quiz_prompts.keys()))
quiz_type = st.selectbox("📝 Quiz Type", ["Multiple Choice", "Short Answer", "True/False"])
num_questions = st.slider("❓ Number of Questions", min_value=3, max_value=15, value=5)
special_notes = st.text_area("📎 Special Notes (optional)")

if st.button("Generate Quiz"):
    if not validate_inputs(subject, grade):
        st.error("Please complete all required fields.")
    else:
        prompt = quiz_prompts[subject].format(
            grade=grade,
            quiz_type=quiz_type,
            num_questions=num_questions,
            special_notes=special_notes or "none"
        )
        with st.spinner("Generating quiz..."):
            quiz = generate_quiz(prompt)
        st.text_area("🧠 Generated Quiz", quiz, height=300)

        # Save and log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quiz_{subject}_{grade}_{timestamp}.txt"
        filepath = os.path.join("outputs/generated_text", filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(quiz)

        with open("logs/download_log.txt", "a", encoding="utf-8") as log:
            log.write(f"[{timestamp}] {filename} | Subject: {subject} | Grade: {grade}\n")

        with open(filepath, "rb") as f:
            st.download_button("📥 Download Quiz", f, file_name=filename)

with st.expander("📚 View Download History"):
    if os.path.exists("logs/download_log.txt"):
        with open("logs/download_log.txt", "r", encoding="utf-8") as log_file:
            st.text_area("Download History Log", log_file.read(), height=200)
    else:
        st.info("No downloads logged yet.")
