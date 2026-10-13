"""
Core scoring logic for the Student Performance AI Dashboard.

Weights:
Attendance  = 20%
Assignment  = 20%
Quiz        = 15%
Midterm     = 20%
Final Exam  = 25%
"""

WEIGHTS = {
    "attendance": 0.20,
    "assignment": 0.20,
    "quiz": 0.15,
    "midterm": 0.20,
    "final": 0.25,
}

LABELS = {
    "attendance": "Attendance",
    "assignment": "Assignment",
    "quiz": "Quiz",
    "midterm": "Midterm",
    "final": "Final Exam",
    "study_hours": "Study Hours Per Day",
}

# (minimum score, grade) - highest first
GRADE_SCALE = [
    (90, "A+"),
    (85, "A"),
    (80, "B+"),
    (70, "B"),
    (60, "C"),
    (50, "D"),
    (0, "F"),
]

# (minimum score, level) - highest first
LEVEL_SCALE = [
    (85, "Excellent"),
    (70, "Good"),
    (50, "Average"),
    (0, "Needs Improvement"),
]


def validate_student(data):
    """
    Check that every required field is present and within range.

    Returns a list of human-readable error messages (empty if valid).
    """

    errors = []

    if "name" in data and not str(data["name"] or "").strip():
        errors.append("Student name is required.")

    ranges = {key: (0, 100) for key in WEIGHTS}
    ranges["study_hours"] = (0, 24)

    for key, (low, high) in ranges.items():
        value = data.get(key)

        if value is None:
            errors.append(f"{LABELS[key]} is required.")

        elif not low <= value <= high:
            errors.append(f"{LABELS[key]} must be between {low} and {high}.")

    return errors


def calculate_performance(data):
    """
    Calculate overall student performance percentage.
    """

    score = sum(data[key] * weight for key, weight in WEIGHTS.items())

    return round(score, 2)


def get_breakdown(data):
    """
    Per-component detail: raw score, weight and weighted contribution.
    """

    return [
        {
            "key": key,
            "label": LABELS[key],
            "score": data[key],
            "weight": weight,
            "contribution": round(data[key] * weight, 2),
        }
        for key, weight in WEIGHTS.items()
    ]


def biggest_opportunity(data):
    """
    The component with the most overall points still available,
    i.e. the largest weight * (100 - score).

    Returns (key, points_available).
    """

    gaps = {
        key: round((100 - data[key]) * weight, 2)
        for key, weight in WEIGHTS.items()
    }
    key = max(gaps, key=gaps.get)

    return key, gaps[key]


def get_performance_level(score):

    for minimum, level in LEVEL_SCALE:
        if score >= minimum:
            return level


def get_grade(score):

    for minimum, grade in GRADE_SCALE:
        if score >= minimum:
            return grade


def next_grade(score):
    """
    The next grade up and the overall score it needs.

    Returns (minimum_score, grade), or None at the top grade.
    """

    higher = [(m, g) for m, g in GRADE_SCALE if m > score]

    return higher[-1] if higher else None


def next_grade_target(data):
    """
    Final exam score needed to reach the next grade up, keeping every
    other component the same.

    Returns (next_grade, required_final_score), or None if the student
    already has the top grade or the next grade is out of reach.
    """

    current = calculate_performance(data)
    upcoming = next_grade(current)

    if not upcoming:
        return None

    minimum, grade = upcoming
    without_final = current - data["final"] * WEIGHTS["final"]
    required = (minimum - without_final) / WEIGHTS["final"]

    if required > 100:
        return None

    return grade, round(max(required, 0), 1)
