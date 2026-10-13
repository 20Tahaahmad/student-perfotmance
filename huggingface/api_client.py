import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "deepseek-ai/DeepSeek-V3-0324")
HF_TIMEOUT = float(os.getenv("HF_TIMEOUT", "60"))

_client = None


def is_configured():
    return bool(HF_TOKEN)


def get_client():
    """
    Create the inference client on first use, so the app can still start
    (and fall back to rule-based summaries) without an HF_TOKEN.
    """

    global _client

    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN was not found in .env")

    if _client is None:
        _client = InferenceClient(
            api_key=HF_TOKEN,
            provider="auto",
            timeout=HF_TIMEOUT
        )

    return _client


def generate_student_summary(student):

    prompt = f"""
Analyze this student's academic performance.

Student Name: {student["name"]}
Attendance: {student["attendance"]}%
Study Hours Per Day: {student["study_hours"]}
Assignment Score: {student["assignment"]}%
Quiz Score: {student["quiz"]}%
Midterm Score: {student["midterm"]}%
Final Exam Score: {student["final"]}%
Overall Performance: {student["performance"]}%

Provide a concise report in Markdown with these bold section headings:

**Performance Summary:**
**Strengths:**
**Weak Areas:**
**Recommendations:**

Use bullet points under each heading except the summary.
Use only the information provided.
Do not invent marks or information.
"""

    response = get_client().chat.completions.create(
        model=HF_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=500,
        temperature=0.3
    )

    return response.choices[0].message.content
