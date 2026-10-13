"""
Rule-based student report.

Used as a fallback when the Hugging Face model is not configured or the
API call fails, so the dashboard always returns an analysis.
"""

from ai_engine.performance import (
    WEIGHTS,
    LABELS,
    get_performance_level,
    next_grade_target,
)

STRONG = 80
WEAK = 60

TIPS = {
    "attendance": "Attend every class; missed sessions are the easiest marks to recover.",
    "assignment": "Start assignments early and review the marking criteria before submitting.",
    "quiz": "Use short daily recall practice to prepare for quizzes.",
    "midterm": "Review midterm mistakes and revisit those topics before the final.",
    "final": "Build a revision timetable and practise with past exam papers.",
}


def generate_rule_based_summary(student):
    """
    Build a markdown report with the same sections as the AI summary.
    """

    performance = student["performance"]
    level = get_performance_level(performance)

    scores = {key: student[key] for key in WEIGHTS}
    strengths = [k for k, v in scores.items() if v >= STRONG]
    weak = [k for k, v in scores.items() if v < WEAK]

    # If nothing is clearly weak, point at the lowest component
    focus = weak or [min(scores, key=scores.get)]

    lines = [
        "**Performance Summary:**",
        f"{student['name']} has an overall performance of {performance}% "
        f"({level}).",
        "",
        "**Strengths:**",
    ]

    if strengths:
        lines += [f"- {LABELS[k]}: {scores[k]}%" for k in strengths]
    else:
        lines.append(f"- No component is at {STRONG}% or above yet.")

    lines += ["", "**Weak Areas:**"]
    lines += [f"- {LABELS[k]}: {scores[k]}%" for k in focus]

    lines += ["", "**Recommendations:**"]
    lines += [f"- {TIPS[k]}" for k in focus]

    hours = student.get("study_hours")
    if hours is not None and hours < 2:
        lines.append(
            f"- Current study time is {hours:g} h/day; "
            "aim for at least 2 focused hours."
        )

    target = next_grade_target(student)
    if target:
        grade, required = target
        lines.append(
            f"- Scoring {required}% on the final exam would raise the "
            f"overall grade to {grade}."
        )

    return "\n".join(lines)
