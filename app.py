import streamlit as st
import requests
import PyPDF2
import os
import re
from dotenv import load_dotenv


# Load Environment Variables
load_dotenv()


# Page Config

st.set_page_config(
    page_title="SkillCatalyst AI | Hiring Intelligence Platform",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS

st.markdown("""
<style>
.main {
    padding-top: 1rem;
}
.block-container {
    padding-top: 2rem;
}
.metric-box {
    background-color: #1f2937;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# Header

st.title("🚀 SkillCatalyst AI")
st.subheader("AI Skill Assessment & Personalized Learning Agent")

st.markdown("---")

st.info(
    "Upload a resume and paste a job description to evaluate candidate-job fit, "
    "identify skill gaps, assess readiness, and generate a personalized roadmap."
)


# Utility Functions


def read_pdf(uploaded_file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except:
        return "Unable to read PDF properly."
    return text


def ask_ai(prompt):
    api_key = os.getenv("OPENROUTER_API_KEY")

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": str(prompt)
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=90
        )

        result = response.json()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            return "API Error: " + str(result)

    except Exception as e:
        return f"Request Failed: {str(e)}"


def extract_score(text):
    match = re.search(r'Match Percentage.*?(\d{1,3})', text, re.IGNORECASE | re.DOTALL)
    if match:
        val = int(match.group(1))
        return min(max(val, 0), 100)

    match2 = re.search(r'(\d{1,3})\s*%', text)
    if match2:
        val = int(match2.group(1))
        return min(max(val, 0), 100)

    return 75



# Input Section

col1, col2 = st.columns(2)

with col1:
    resume = st.file_uploader("📄 Upload Resume PDF", type=["pdf"])

with col2:
    jd = st.text_area("💼 Paste Job Description", height=260)

# Analyze Button

if st.button("Analyze Candidate", use_container_width=True):

    if resume and jd:

       
        # Read Resume
       
        with st.spinner("📄 Reading Resume..."):
            resume_text = read_pdf(resume)

        
        # Analysis Prompt
       
        prompt = f"""
You are a senior recruiter and hiring manager.

Evaluate candidate against the job description.

Return in markdown:

## Final Hiring Verdict

## Match Percentage (0-100)

## Top Matching Skills
(Bullets)

## Missing Skills
(Bullets)

## Candidate Strengths

## Hiring Risks

## Hire Readiness Score (0-100)

## 5 Personalized Interview Questions

## Final Recommendation
Reject / Consider / Strong Hire

Resume:
{resume_text}

Job Description:
{jd}
"""

        # AI Analysis

        with st.spinner("🤖 Evaluating Candidate..."):
            result = ask_ai(prompt)

        st.success("Analysis Completed Successfully!")

       
        # Extract Score
       
        score = extract_score(result)

       
        # Dashboard
       
        st.markdown("## 📊 Recruiter Dashboard")

        d1, d2, d3, d4 = st.columns(4)

        d1.metric("Match Score", f"{score}%")
        d2.metric("Resume Parsed", "Yes")
        d3.metric("Risk Level", "Low" if score > 70 else "Medium")
        d4.metric("Interview Ready", "Yes" if score > 65 else "Needs Prep")

        st.progress(score / 100)

       
        # Main Output
       
        st.markdown("## 🧠 Candidate Evaluation")
        st.markdown(result)

       
        # Roadmap Prompt  
        roadmap_prompt = f"""
Based on this candidate evaluation:

{result}

Create a practical 30-day personalized learning roadmap.

Format:

## Week 1
Topics
Daily Time
Free Resources

## Week 2

## Week 3

## Week 4

## Final Mini Project

Keep roadmap realistic and beginner-friendly.
"""

        with st.spinner("📚 Creating Learning Roadmap..."):
            roadmap = ask_ai(roadmap_prompt)

        st.markdown("## 📚 Personalized Learning Roadmap")
        st.markdown(roadmap)

       
        # Career Suggestion Prompt
       
        career_prompt = f"""
Based on this resume and candidate evaluation:

{resume_text}

{result}

Suggest top 3 suitable job roles for the next 6 months with one-line reason each.
"""

        with st.spinner("🚀 Finding Career Paths..."):
            career = ask_ai(career_prompt)

        st.markdown("## 🚀 Recommended Career Paths")
        st.markdown(career)

       
        # Download Report
    
        report = f"""
SKILLCATALYST AI REPORT

=========================
CANDIDATE ANALYSIS
=========================

{result}

=========================
LEARNING ROADMAP
=========================

{roadmap}

=========================
CAREER PATHS
=========================

{career}
"""

        st.download_button(
            label="📥 Download Full Report",
            data=report,
            file_name="SkillCatalyst_Report.txt",
            mime="text/plain",
            use_container_width=True
        )

    else:
        st.warning("Please upload resume and paste job description.")
