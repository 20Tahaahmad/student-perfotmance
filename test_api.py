"""
Live Hugging Face API check. Skipped by default because it makes a real
(paid / rate-limited) request. Run with:

    RUN_API_TESTS=1 pytest test_api.py -s
"""

import os

import pytest

from huggingface.api_client import generate_student_summary, is_configured

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_API_TESTS") != "1" or not is_configured(),
    reason="set RUN_API_TESTS=1 and HF_TOKEN to call the live API"
)


def test_generate_student_summary():
    student = {
        "name": "Ali",
        "attendance": 90,
        "study_hours": 5,
        "assignment": 85,
        "quiz": 80,
        "midterm": 75,
        "final": 88,
        "performance": 84
    }

    summary = generate_student_summary(student)

    print("\n===== AI STUDENT SUMMARY =====\n")
    print(summary)

    assert summary and summary.strip()
