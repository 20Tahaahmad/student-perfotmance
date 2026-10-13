import os
import io
import csv
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ai_engine.performance import (
    LABELS,
    WEIGHTS,
    calculate_performance,
    get_performance_level,
    get_grade,
    get_breakdown,
    next_grade,
    next_grade_target,
    biggest_opportunity,
    validate_student,
)
from ai_engine.summary import generate_rule_based_summary, TIPS
from huggingface.api_client import generate_student_summary, is_configured

# Streamlit replacement for the original Dash app.
st.set_page_config(
    page_title="Student Performance AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

SCORE_KEYS = ["attendance", "study_hours", "assignment", "quiz", "midterm", "final"]
FIELD_CONFIG = [
    ("attendance", "Attendance (%)", 0.0, 100.0, 1.0, 75.0),
    ("study_hours", "Study hours per day", 0.0, 24.0, 0.5, 2.0),
    ("assignment", "Assignment score (%)", 0.0, 100.0, 1.0, 75.0),
    ("quiz", "Quiz score (%)", 0.0, 100.0, 1.0, 75.0),
    ("midterm", "Midterm score (%)", 0.0, 100.0, 1.0, 75.0),
    ("final", "Final exam score (%)", 0.0, 100.0, 1.0, 75.0),
]
RECOMMENDED_STUDY_HOURS = 2
MAX_HISTORY = 100

SAMPLE_STUDENTS = [
    ["Ali Khan", 90, 5, 85, 80, 75, 88],
    ["Sara Ahmed", 97, 6, 94, 91, 89, 95],
    ["Bilal Raza", 72, 1.5, 64, 48, 58, 61],
    ["Hina Malik", 55, 1, 42, 38, 45, 40],
]

LEVEL_COLORS = {
    "Excellent": "#22c55e",
    "Good": "#38bdf8",
    "Average": "#f59e0b",
    "Needs Improvement": "#fb7185",
    "Poor": "#ef4444",
}
DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
.stApp {font-family:Inter,sans-serif;background:radial-gradient(ellipse at 10% 5%,rgba(99,102,241,.18),transparent 34%),linear-gradient(135deg,#0b1020,#10182b 60%,#0b1220);color:#f5f7ff}
.block-container{max-width:1400px;padding-top:1.4rem;padding-bottom:3rem}
[data-testid="stHeader"]{background:transparent}
.hero{padding:1.8rem 0 1.2rem}
.eyebrow{color:#a5b4fc;text-transform:uppercase;letter-spacing:.12em;font-size:.76rem;font-weight:800}
.hero h1{font-size:clamp(2.2rem,4vw,3.5rem);font-weight:800;letter-spacing:-.04em;color:#fff;margin:.5rem 0}
.hero p{color:#aab6d0;max-width:800px;line-height:1.7}
.gradient{background:linear-gradient(90deg,#a78bfa,#38bdf8);-webkit-background-clip:text;color:transparent}
.glass{border:1px solid rgba(167,184,220,.17);border-radius:20px;padding:22px;background:linear-gradient(145deg,rgba(25,35,60,.92),rgba(14,22,40,.9));margin-bottom:16px}
.section-title{font-size:1.08rem;font-weight:800;color:#f5f7ff;margin-bottom:15px}
.metric{border:1px solid rgba(167,184,220,.17);border-radius:16px;padding:16px;background:rgba(255,255,255,.035);margin-bottom:12px}
.metric-label{color:#aab6d0;font-size:.78rem}
.metric-value{font-size:1.65rem;font-weight:800;color:#fff;overflow-wrap:anywhere}
.muted{color:#aab6d0;font-size:.86rem;line-height:1.65}
.pill{display:inline-block;border-radius:999px;padding:5px 10px;font-size:.75rem;font-weight:800}
.stApp p,.stApp li,.stApp label,.stApp input,.stApp button,.stApp h1,.stApp h2,.stApp h3{font-family:Inter,sans-serif}
.stApp p,.stApp li,.stApp h1,.stApp h2,.stApp h3,.stApp strong{color:#e8ecf8}
.report-title{font-size:1.5rem;font-weight:800;color:#fff}
hr{border-color:rgba(167,184,220,.17)}

/* Glass cards (bordered st.container with key "glass_*") */
[class*="st-key-glass"]{border:1px solid rgba(167,184,220,.17)!important;border-radius:20px!important;padding:22px!important;background:linear-gradient(145deg,rgba(25,35,60,.92),rgba(14,22,40,.9))}

/* Widget labels: always readable on the dark background */
[data-testid="stWidgetLabel"] p,[data-testid="stWidgetLabel"] label{color:#c7d2fe!important;font-weight:600;font-size:.88rem}

/* Inputs */
div[data-testid="stTextInput"] input,div[data-testid="stNumberInput"] input{background:#121a2f!important;color:#f5f7ff!important;-webkit-text-fill-color:#f5f7ff;font-weight:500}
div[data-testid="stTextInput"] input::placeholder{color:#6b7896!important;-webkit-text-fill-color:#6b7896}
div[data-testid="stTextInput"]>div>div,div[data-testid="stNumberInput"]>div>div{background:#121a2f!important;border-color:rgba(167,184,220,.22)!important;border-radius:11px}
div[data-testid="stNumberInput"] button{background:#18213a!important;color:#c7d2fe!important}

/* Alerts (info / success / error / warning) */
[data-testid="stAlert"] p,[data-testid="stAlert"] li,[data-testid="stAlert"] strong{color:#f5f7ff!important}

/* Buttons */
.stButton button,.stDownloadButton button{border-radius:11px;font-weight:700;min-height:42px;background:#18213a;color:#e8ecf8;border:1px solid rgba(167,184,220,.25)}
.stButton button:hover,.stDownloadButton button:hover{border-color:#818cf8;color:#fff}
.stButton button[kind="primary"]{background:linear-gradient(90deg,#6366f1,#3b82f6);border:0;color:#fff;box-shadow:0 8px 22px rgba(99,102,241,.35)}
.stButton button[kind="primary"]:hover{filter:brightness(1.08);color:#fff}
.stButton button p,.stDownloadButton button p{color:inherit!important}

/* Sidebar */
[data-testid="stSidebar"]{background:#0e1528!important;border-right:1px solid rgba(167,184,220,.12)}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] strong{color:#e8ecf8!important}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,[data-testid="stCaptionContainer"] p{color:#aab6d0!important}
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def make_breakdown_figure(student, performance):
    breakdown = get_breakdown(student)
    labels, values = [], []
    for item in breakdown:
        labels.append(str(item.get("label", item.get("key", "Score"))))
        values.append(safe_float(item.get("score", 0)))
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=values, marker_color="#818cf8",
        text=[f"{v:g}%" for v in values], textposition="outside",
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        height=340, margin=dict(l=12, r=12, t=24, b=20),
        yaxis=dict(range=[0, 110], title="Score (%)", gridcolor="rgba(180,195,225,.12)"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dbe4ff"), showlegend=False,
    )
    return fig, breakdown


def make_history_figure(history):
    df = pd.DataFrame(history)
    if df.empty:
        return go.Figure()
    # Ranked bars, best student on top, with the class average as a reference line
    df = df.sort_values("performance", ascending=True)
    average = df["performance"].astype(float).mean()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["performance"], y=df["name"], orientation="h", width=0.55,
        marker=dict(color="#818cf8", cornerradius=4),
        text=[f"{v:g}%" for v in df["performance"]], textposition="outside",
        customdata=df[["grade", "level"]],
        hovertemplate="<b>%{y}</b><br>%{x:.1f}% · Grade %{customdata[0]} · %{customdata[1]}<extra></extra>",
    ))
    fig.add_vline(
        x=average, line=dict(color="#aab6d0", width=1), layer="below",
        annotation_text=f"Average {average:.1f}%", annotation_position="top",
        annotation_font=dict(color="#aab6d0", size=12),
    )
    fig.update_layout(
        height=max(180, 46 * len(df) + 80), margin=dict(l=10, r=40, t=30, b=20),
        xaxis=dict(range=[0, 105], ticksuffix="%", gridcolor="rgba(180,195,225,.12)", zeroline=False),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dbe4ff"), showlegend=False,
    )
    return fig


def analyze(student):
    performance = calculate_performance(student)
    student["performance"] = performance
    grade = get_grade(performance)
    level = get_performance_level(performance)
    source = "offline"
    if is_configured():
        try:
            summary = generate_student_summary(student)
            source = "ai"
        except Exception:
            summary = generate_rule_based_summary(student)
            source = "fallback"
    else:
        summary = generate_rule_based_summary(student)
    return {
        "student": student,
        "performance": performance,
        "grade": grade,
        "level": level,
        "summary": summary,
        "source": source,
        "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def report_markdown(result):
    student = result["student"]
    return (
        f"# Student report: {student['name']}\n\n"
        f"_Overall {student['performance']:g}% · Grade {result['grade']} · "
        f"{result['level']} · {result['analyzed_at']}_\n\n"
        f"{result['summary']}\n"
    )


if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result = None

# Header
st.markdown(
    '<div class="hero"><div class="eyebrow">✦ AI-powered learning insights</div>'
    '<h1>Student Performance <span class="gradient">AI</span></h1>'
    '<p>Analyze student performance, understand strengths and gaps, and get practical recommendations to improve results.</p></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🎓 Student Performance AI")
    st.caption("Enter scores or load a sample student.")
    if st.button("Load sample student", use_container_width=True):
        sample_index = st.session_state.get("sample_index", -1) + 1
        sample_index %= len(SAMPLE_STUDENTS)
        st.session_state.sample_index = sample_index
        sample = SAMPLE_STUDENTS[sample_index]
        st.session_state.student_name = sample[0]
        for i, key in enumerate(SCORE_KEYS):
            st.session_state[f"score_{key}"] = float(sample[i + 1])
        st.rerun()
    if st.button("Clear form", use_container_width=True):
        for key in ["student_name"] + [f"score_{k}" for k in SCORE_KEYS]:
            st.session_state.pop(key, None)
        st.rerun()
    st.divider()
    st.markdown("### Scoring guide")
    st.caption("Score fields are percentages from 0–100. Study hours are hours per day.")
    st.markdown(f"Recommended study time: **{RECOMMENDED_STUDY_HOURS} hours/day**")
    st.caption("AI summary uses Hugging Face when configured; otherwise a rule-based summary is generated.")

form_col, live_col = st.columns([1.1, 0.9], gap="large")

with form_col:
    with st.container(border=True, key="glass_form"):
        st.markdown('<div class="section-title">📝 Student details & scores</div>', unsafe_allow_html=True)
        name = st.text_input("Student name", key="student_name", placeholder="Enter student name")
        first_row = st.columns(2)
        values = {}
        for index, (key, label, minimum, maximum, step, default) in enumerate(FIELD_CONFIG):
            # Seed the default via session state only, so "Load sample" doesn't
            # trigger Streamlit's "default value + Session State" warning
            st.session_state.setdefault(f"score_{key}", float(default))
            with first_row[index % 2]:
                values[key] = st.number_input(
                    label,
                    min_value=float(minimum),
                    max_value=float(maximum),
                    step=float(step),
                    key=f"score_{key}",
                )
        student = {"name": name.strip(), **values}
        live_errors = validate_student(student)
        if name.strip() and not live_errors:
            live_performance = calculate_performance(student)
            st.info(f"⚡ Live estimate: **{live_performance:g}%** · Grade **{get_grade(live_performance)}**")
        analyze_clicked = st.button("✨ Analyze performance", type="primary", use_container_width=True)

    if analyze_clicked:
        errors = validate_student(student)
        if not name.strip():
            errors = list(errors or []) + ["Student name is required."]
        if errors:
            st.error("Please fix the following:\n\n" + "\n".join(f"- {error}" for error in errors))
        else:
            try:
                with st.spinner("Analyzing student performance…"):
                    result = analyze(dict(student))
                st.session_state.result = result
                entry = {
                    **student,
                    "performance": result["performance"],
                    "grade": result["grade"],
                    "level": result["level"],
                    "analyzed_at": result["analyzed_at"],
                }
                history = [
                    item for item in st.session_state.history
                    if item["name"].strip().lower() != name.strip().lower()
                ]
                st.session_state.history = ([entry] + history)[:MAX_HISTORY]
                st.success(f"{name}'s results were added to History.")
            except Exception as error:
                st.error(f"Analysis failed: {error}")

with live_col, st.container(border=True, key="glass_overview"):
    st.markdown('<div class="section-title">📊 Score overview</div>', unsafe_allow_html=True)
    if name.strip() and not live_errors:
        try:
            score = calculate_performance(student)
            level = get_performance_level(score)
            grade = get_grade(score)
            color = LEVEL_COLORS.get(str(level), "#818cf8")
            st.markdown(
                f'<div class="metric"><div class="metric-label">Estimated overall performance</div>'
                f'<div class="metric-value" style="color:{color}">{score:.1f}%</div>'
                f'<div class="muted">Grade {grade} · {level}</div></div>',
                unsafe_allow_html=True,
            )
            st.progress(max(0.0, min(1.0, score / 100)))
            breakdown_fig, breakdown = make_breakdown_figure(student, score)
            st.plotly_chart(
                breakdown_fig,
                use_container_width=True,
                config={"displayModeBar": False},
                key="breakdown_chart",
            )
        except Exception as error:
            st.warning(f"Could not calculate preview: {error}")
    else:
        st.markdown(
            '<div style="padding:2.5rem 1rem;text-align:center"><div style="font-size:2.5rem">📈</div>'
            '<div class="report-title">Your report appears here</div>'
            '<p class="muted">Enter a name and valid scores to see a live estimate.</p></div>',
            unsafe_allow_html=True,
        )

# Analysis report
result = st.session_state.result
if result:
    st.markdown("---")
    student_result = result["student"]
    st.markdown('<div class="section-title">📋 Performance report</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="glass"><div class="report-title">{student_result["name"]}</div>'
        f'<div class="muted">Analyzed {result["analyzed_at"]}</div></div>',
        unsafe_allow_html=True,
    )

    performance = float(result["performance"])
    grade = result["grade"]
    level = result["level"]
    upcoming = next_grade(performance)
    target = next_grade_target(student_result)
    hours = float(student_result["study_hours"])

    kpi_cols = st.columns(4)
    kpis = [
        ("Overall score", f"{performance:.1f}%", level),
        ("Current grade", str(grade), "Academic grade"),
        ("Next grade", f"+{round(upcoming[0] - performance, 2):g}" if upcoming else "—",
         f"Points to {upcoming[1]}" if upcoming else "Top grade reached"),
        ("Study hours", f"{hours:g} h/day",
         "On target" if hours >= RECOMMENDED_STUDY_HOURS else "Below recommended"),
    ]
    for col, (label, value, hint) in zip(kpi_cols, kpis):
        with col:
            st.markdown(
                f'<div class="metric"><div class="metric-label">{label}</div>'
                f'<div class="metric-value">{value}</div><div class="metric-label">{hint}</div></div>',
                unsafe_allow_html=True,
            )

    left_report, right_report = st.columns([1, 1], gap="large")
    with left_report, st.container(border=True, key="glass_breakdown"):
        st.markdown('<div class="section-title">📈 Score breakdown</div>', unsafe_allow_html=True)
        figure, breakdown = make_breakdown_figure(student_result, performance)
        st.plotly_chart(
            figure,
            use_container_width=True,
            config={"displayModeBar": False},
            key="performance_chart",
        )
        try:
            breakdown_df = pd.DataFrame(breakdown)
            st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
        except Exception:
            pass

    with right_report, st.container(border=True, key="glass_insights"):
        st.markdown('<div class="section-title">💡 Insights & recommendations</div>', unsafe_allow_html=True)
        try:
            best = max(breakdown, key=lambda item: safe_float(item.get("score")))
            worst = min(breakdown, key=lambda item: safe_float(item.get("score")))
            lever, points = biggest_opportunity(student_result)
            st.markdown(f"**Strongest area:** {best.get('label', best.get('key', 'Score'))} — {best.get('score', 0):g}%")
            st.caption("Keep this up; it anchors the overall score.")
            st.markdown(f"**Needs focus:** {worst.get('label', worst.get('key', 'Score'))} — {worst.get('score', 0):g}%")
            st.caption(TIPS.get(worst.get("key"), "Practice this area consistently and review mistakes."))
            st.markdown(f"**Biggest opportunity:** {LABELS.get(lever, lever) if isinstance(LABELS, dict) else lever} — up to +{points:g} points")
            st.caption("Focus on the highest-impact area to improve the overall result.")
            if target:
                st.markdown(f"**Final exam target:** {target[1]:g}% to reach grade {target[0]}.")
            elif upcoming:
                st.markdown(f"**Next grade:** {upcoming[1]} starts at {upcoming[0]}%.")
        except Exception as error:
            st.caption(f"Some insights could not be generated: {error}")

    with st.container(border=True, key="glass_summary"):
        st.markdown('<div class="section-title">🧠 Personalized summary</div>', unsafe_allow_html=True)
        source_label = {
            "ai": "✨ AI-generated summary",
            "fallback": "⚠️ AI unavailable — rule-based summary",
            "offline": "⚙️ Rule-based summary (offline mode)",
        }.get(result["source"], "Summary")
        st.caption(source_label)
        st.write(result["summary"])
        st.download_button(
            "⬇️ Download student report",
            data=report_markdown(result),
            file_name=f"{student_result['name'].strip().replace(' ', '_')}_report.md",
            mime="text/markdown",
            use_container_width=False,
        )

# History and export
st.markdown("---")
history = st.session_state.history
history_head_left, history_head_right = st.columns([3, 1])
with history_head_left:
    st.markdown('<div class="section-title">🕘 Student history</div>', unsafe_allow_html=True)
with history_head_right:
    if st.button("🗑 Clear history", use_container_width=True):
        st.session_state.history = []
        st.rerun()

if history:
    hist_df = pd.DataFrame(history)
    if "performance" in hist_df.columns:
        h1, h2, h3 = st.columns(3)
        with h1:
            st.markdown(f'<div class="metric"><div class="metric-label">Students analyzed</div><div class="metric-value">{len(history)}</div></div>', unsafe_allow_html=True)
        with h2:
            average = hist_df["performance"].astype(float).mean()
            st.markdown(f'<div class="metric"><div class="metric-label">Class average</div><div class="metric-value">{average:.1f}%</div><div class="metric-label">Grade {get_grade(average)}</div></div>', unsafe_allow_html=True)
        with h3:
            top = hist_df.sort_values("performance", ascending=False).iloc[0]
            st.markdown(f'<div class="metric"><div class="metric-label">Top performer</div><div class="metric-value">{top["name"]}</div><div class="metric-label">{top["performance"]:.1f}% · {top["grade"]}</div></div>', unsafe_allow_html=True)
        st.plotly_chart(
            make_history_figure(history),
            use_container_width=True,
            config={"displayModeBar": False},
            key="history_chart",
        )
    st.dataframe(hist_df, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Export history as CSV",
        data=hist_df.to_csv(index=False).encode("utf-8"),
        file_name="student_performance.csv",
        mime="text/csv",
    )
else:
    st.info("No students analyzed yet. Your saved results will appear here.")

st.markdown(
    '<div style="text-align:center;color:#8290ae;font-size:.8rem;padding:30px 0">'
    'Student Performance AI · Built with Streamlit, Plotly and Hugging Face</div>',
    unsafe_allow_html=True,
)
