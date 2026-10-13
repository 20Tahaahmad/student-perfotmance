# Student Performance AI Dashboard

A Dash web app that scores a student's performance, assigns a grade, and
writes an analysis using a Hugging Face hosted LLM.

## Features

- Light / dark theme toggle (remembered per browser)
- Live score estimate while typing, plus sample students to try
- Overview: animated score ring, KPI tiles (grade, points to next grade,
  final exam needed, study hours) and insights (strongest area, needs
  focus, biggest opportunity)
- Score breakdown chart with a table view
- AI report tab with copy and Markdown download
- History tab: every analyzed student is saved in the browser, with class
  stats, a ranking chart and CSV export
- Rule-based fallback report when no API token is set or the API call fails
- Input validation with clear error messages
- Responsive layout for phones, tablets and desktops

## Project layout

```
app.py                  Dash app and callbacks
ui/layout.py            Page layout and display components
ui/charts.py            Plotly figures (light & dark themed)
assets/style.css        Theme and styling
ai_engine/performance.py  Scoring, grades, validation, insights
ai_engine/summary.py      Rule-based report
huggingface/api_client.py AI report via Hugging Face
```

## Scoring

| Component  | Weight |
|------------|--------|
| Attendance | 20%    |
| Assignment | 20%    |
| Quiz       | 15%    |
| Midterm    | 20%    |
| Final Exam | 25%    |

Grades: A+ ≥ 90, A ≥ 85, B+ ≥ 80, B ≥ 70, C ≥ 60, D ≥ 50, F < 50.
Study hours are used in the analysis but not in the score.

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```
HF_TOKEN=your_hugging_face_token
# Optional
HF_MODEL=deepseek-ai/DeepSeek-V3-0324
HF_TIMEOUT=60
DASH_DEBUG=true
PORT=8050
```

## Run

```bash
python app.py
```

Then open http://127.0.0.1:8050.

## Tests

```bash
pytest                              # unit tests
RUN_API_TESTS=1 pytest test_api.py -s   # live Hugging Face call
```
