import pytest

from ai_engine.performance import (
    calculate_performance,
    get_performance_level,
    get_grade,
    get_breakdown,
    biggest_opportunity,
    next_grade,
    next_grade_target,
    validate_student
)
from ai_engine.summary import generate_rule_based_summary


def make_student(**overrides):
    student = {
        "name": "Ali",
        "attendance": 90,
        "study_hours": 5,
        "assignment": 85,
        "quiz": 80,
        "midterm": 75,
        "final": 88
    }
    student.update(overrides)
    return student


def test_calculate_performance():
    assert calculate_performance(make_student()) == 84.0


def test_breakdown_sums_to_performance():
    student = make_student()
    total = sum(item["contribution"] for item in get_breakdown(student))
    assert round(total, 2) == calculate_performance(student)


@pytest.mark.parametrize(
    "score, grade",
    [(100, "A+"), (90, "A+"), (89.99, "A"), (85, "A"), (80, "B+"),
     (70, "B"), (60, "C"), (50, "D"), (49.99, "F"), (0, "F")]
)
def test_get_grade(score, grade):
    assert get_grade(score) == grade


@pytest.mark.parametrize(
    "score, level",
    [(85, "Excellent"), (70, "Good"), (50, "Average"), (49, "Needs Improvement")]
)
def test_get_performance_level(score, level):
    assert get_performance_level(score) == level


def test_validate_student_accepts_valid_input():
    assert validate_student(make_student()) == []


def test_validate_student_reports_problems():
    errors = validate_student(
        make_student(name="  ", quiz=None, final=150, study_hours=30)
    )
    assert "Student name is required." in errors
    assert "Quiz is required." in errors
    assert "Final Exam must be between 0 and 100." in errors
    assert "Study Hours Per Day must be between 0 and 24." in errors


def test_next_grade_target():
    # 84% now (B+); A needs 85%, i.e. 4 more final-exam points
    assert next_grade_target(make_student()) == ("A", 92.0)


def test_next_grade_target_top_grade():
    perfect = make_student(attendance=100, assignment=100, quiz=100,
                           midterm=100, final=100)
    assert next_grade_target(perfect) is None


def test_next_grade_target_out_of_reach():
    # Even 100% on the final can't lift this student to the next grade
    low = make_student(attendance=0, assignment=0, quiz=0, midterm=0, final=10)
    assert next_grade_target(low) is None


def test_next_grade():
    assert next_grade(84) == (85, "A")
    assert next_grade(49.5) == (50, "D")
    assert next_grade(95) is None


def test_biggest_opportunity():
    # Final: (100 - 50) * 0.25 = 12.5 points available, the most of any component
    student = make_student(final=50)
    assert biggest_opportunity(student) == ("final", 12.5)


def test_rule_based_summary_sections():
    student = make_student(quiz=40)
    student["performance"] = calculate_performance(student)
    summary = generate_rule_based_summary(student)

    for heading in ["Performance Summary", "Strengths", "Weak Areas", "Recommendations"]:
        assert f"**{heading}:**" in summary

    assert "Quiz: 40%" in summary
