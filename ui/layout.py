"""
Page layout and the display components the callbacks fill in.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc

# (id, label, icon, max, placeholder, step, unit)
ENGAGEMENT_FIELDS = [
    ("attendance", "Attendance", "bi-calendar-check", 100, "90", 1, "%"),
    ("study-hours", "Study hours / day", "bi-hourglass-split", 24, "5", 0.5, "hrs"),
]

ASSESSMENT_FIELDS = [
    ("assignment", "Assignment", "bi-journal-text", 100, "85", 1, "%"),
    ("quiz", "Quiz", "bi-patch-question", 100, "80", 1, "%"),
    ("midterm", "Midterm", "bi-clipboard-data", 100, "75", 1, "%"),
    ("final", "Final exam", "bi-mortarboard", 100, "88", 1, "%"),
]

FIELDS = ENGAGEMENT_FIELDS + ASSESSMENT_FIELDS

# level -> (icon, tone)
LEVEL_STYLE = {
    "Excellent": ("bi-trophy-fill", "good"),
    "Good": ("bi-hand-thumbs-up-fill", "info"),
    "Average": ("bi-dash-circle-fill", "warning"),
    "Needs Improvement": ("bi-exclamation-triangle-fill", "critical"),
}


def icon(name, className=""):
    return html.I(className=f"bi {name} {className}".strip())


# ---------------------------------------------------------------- form

def number_field(field_id, label, icon_name, maximum, placeholder, step, unit):

    return dbc.Col(
        [
            dbc.Label(
                [icon(icon_name, "me-2"), label],
                html_for=field_id,
                className="field-label"
            ),
            dbc.InputGroup(
                [
                    dbc.Input(
                        id=field_id,
                        type="number",
                        min=0,
                        max=maximum,
                        step=step,
                        placeholder=placeholder,
                        inputmode="decimal"
                    ),
                    dbc.InputGroupText(unit)
                ]
            )
        ],
        xs=12,
        sm=6,
        className="mb-3"
    )


def section_title(text):
    return html.Div(text, className="section-title")


def student_form():

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H2("Student details", className="card-heading"),
                            html.P(
                                "Enter scores to get a grade and analysis.",
                                className="text-secondary-soft mb-0"
                            )
                        ]
                    ),
                    dbc.Button(
                        [icon("bi-magic", "me-1"), "Try a sample"],
                        id="sample-button",
                        color="link",
                        size="sm",
                        className="btn-ghost"
                    )
                ],
                className="d-flex justify-content-between align-items-start mb-4 gap-2"
            ),

            section_title("Student"),
            dbc.Label(
                [icon("bi-person", "me-2"), "Name"],
                html_for="student-name",
                className="field-label"
            ),
            dbc.Input(
                id="student-name",
                type="text",
                placeholder="e.g. Ali Khan",
                className="mb-4",
                autoComplete="off"
            ),

            section_title("Engagement"),
            dbc.Row([number_field(*f) for f in ENGAGEMENT_FIELDS], className="mb-2"),

            section_title("Assessments"),
            dbc.Row([number_field(*f) for f in ASSESSMENT_FIELDS]),

            html.Div(id="live-estimate", className="live-estimate"),

            html.Div(id="form-errors"),

            dbc.Button(
                [icon("bi-stars", "me-2"), "Analyze performance"],
                id="analyze-button",
                color="primary",
                size="lg",
                className="w-100 mb-2 btn-analyze"
            ),

            dbc.Button(
                [icon("bi-arrow-counterclockwise", "me-2"), "Clear form"],
                id="clear-button",
                color="secondary",
                outline=True,
                className="w-100"
            ),

            html.P(
                [
                    icon("bi-info-circle", "me-1"),
                    "Weights: attendance 20%, assignment 20%, quiz 15%, "
                    "midterm 20%, final 25%. Study hours inform the "
                    "analysis only."
                ],
                className="form-note"
            )
        ],
        className="panel p-4 form-panel"
    )


# ---------------------------------------------------------------- overview

def empty_state(title, text, icon_name="bi-bar-chart-line"):

    return html.Div(
        [
            html.Div(icon(icon_name), className="empty-icon"),
            html.H3(title, className="empty-title"),
            html.P(text, className="empty-text")
        ],
        className="empty-state"
    )


def score_ring(performance, level):

    icon_name, tone = LEVEL_STYLE[level]

    return html.Div(
        [
            html.Div(
                html.Div(
                    [
                        html.Div(f"{performance:g}", className="ring-value"),
                        html.Div("overall %", className="ring-caption")
                    ],
                    className="ring-inner"
                ),
                className=f"score-ring tone-{tone}",
                style={"--pct": performance}
            ),
            html.Div(
                [icon(icon_name, "me-2"), level],
                className=f"level-pill tone-{tone}"
            )
        ],
        className="ring-wrap"
    )


def kpi_tile(label, value, icon_name, hint=None, tone="accent"):

    return html.Div(
        [
            html.Div(
                [
                    html.Span(label, className="kpi-label"),
                    html.Span(icon(icon_name), className=f"kpi-icon tone-{tone}")
                ],
                className="d-flex justify-content-between align-items-center"
            ),
            html.Div(value, className="kpi-value"),
            html.Div(hint, className="kpi-hint") if hint else None
        ],
        className="kpi-tile"
    )


def insight_card(title, headline, text, icon_name, tone):

    return dbc.Col(
        html.Div(
            [
                html.Div(icon(icon_name), className=f"insight-icon tone-{tone}"),
                html.Div(
                    [
                        html.Div(title, className="insight-title"),
                        html.Div(headline, className="insight-headline"),
                        html.Div(text, className="insight-text")
                    ]
                )
            ],
            className="insight-card"
        ),
        xs=12,
        md=4,
        className="mb-3"
    )


def breakdown_table(breakdown, overall):

    rows = [
        html.Tr(
            [
                html.Td(item["label"]),
                html.Td(f"{item['score']:g}%", className="text-end"),
                html.Td(f"{item['weight'] * 100:.0f}%", className="text-end"),
                html.Td(f"{item['contribution']:g}", className="text-end"),
            ]
        )
        for item in breakdown
    ]

    rows.append(
        html.Tr(
            [
                html.Th("Overall"),
                html.Td(),
                html.Td("100%", className="text-end"),
                html.Th(f"{overall:g}", className="text-end"),
            ]
        )
    )

    return dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Component"),
                        html.Th("Score", className="text-end"),
                        html.Th("Weight", className="text-end"),
                        html.Th("Points", className="text-end"),
                    ]
                )
            ),
            html.Tbody(rows)
        ],
        size="sm",
        className="data-table mb-0"
    )


def chart_card(title, subtitle, graph_id, table_id, extra=None):

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H3(title, className="card-heading"),
                            html.P(subtitle, className="text-secondary-soft mb-0")
                        ]
                    ),
                    extra
                ],
                className="d-flex justify-content-between align-items-start gap-2 mb-2"
            ),
            dcc.Graph(
                id=graph_id,
                config={"displayModeBar": False, "responsive": True}
            ),
            html.Details(
                [
                    html.Summary("Show as table"),
                    html.Div(id=table_id, className="mt-2")
                ],
                className="table-toggle"
            )
        ],
        className="panel p-4 mb-4"
    )


def overview_tab():

    return html.Div(
        [
            html.Div(
                empty_state(
                    "No analysis yet",
                    "Fill in the form, or click “Try a sample”, then "
                    "press Analyze to see results here."
                ),
                id="overview-empty"
            ),

            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    [
                                        html.Div(id="student-heading"),
                                        html.Div(id="score-ring")
                                    ],
                                    className="panel p-4 h-100"
                                ),
                                xs=12,
                                md=5,
                                className="mb-4"
                            ),
                            dbc.Col(
                                html.Div(id="kpi-grid", className="kpi-grid h-100"),
                                xs=12,
                                md=7,
                                className="mb-4"
                            )
                        ]
                    ),

                    dbc.Row(id="insights"),

                    chart_card(
                        "Score breakdown",
                        "Each component's score; hover a bar for its "
                        "weight and points added.",
                        "breakdown-chart",
                        "breakdown-table"
                    )
                ],
                id="overview-content",
                style={"display": "none"}
            )
        ]
    )


# ---------------------------------------------------------------- report

def report_tab():

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H3("Student report", className="card-heading mb-1"),
                            html.Div(id="summary-source")
                        ]
                    ),
                    html.Div(
                        [
                            dcc.Clipboard(
                                id="copy-report",
                                target_id="ai-summary",
                                title="Copy report",
                                className="btn btn-outline-secondary btn-sm icon-btn"
                            ),
                            dbc.Button(
                                [icon("bi-download", "me-1"), "Download"],
                                id="download-report-button",
                                color="secondary",
                                outline=True,
                                size="sm",
                                disabled=True
                            )
                        ],
                        className="d-flex gap-2"
                    )
                ],
                className="d-flex justify-content-between align-items-start gap-2 mb-3"
            ),

            dcc.Markdown(
                "Run an analysis to generate the student report.",
                id="ai-summary",
                className="ai-summary"
            ),

            dcc.Download(id="download-report")
        ],
        className="panel p-4 mb-4"
    )


# ---------------------------------------------------------------- history

def history_tab():

    return html.Div(
        [
            html.Div(
                empty_state(
                    "No students saved yet",
                    "Every analysis is saved here so you can compare "
                    "students. Results stay in this browser.",
                    "bi-people"
                ),
                id="history-empty"
            ),

            html.Div(
                [
                    html.Div(id="history-stats", className="kpi-grid kpi-grid-3 mb-4"),

                    chart_card(
                        "Class ranking",
                        "Overall performance of each analyzed student.",
                        "history-chart",
                        "history-table",
                        extra=html.Div(
                            [
                                dbc.Button(
                                    [icon("bi-filetype-csv", "me-1"), "Export CSV"],
                                    id="export-history-button",
                                    color="secondary",
                                    outline=True,
                                    size="sm"
                                ),
                                dcc.ConfirmDialogProvider(
                                    dbc.Button(
                                        [icon("bi-trash3", "me-1"), "Clear"],
                                        color="danger",
                                        outline=True,
                                        size="sm"
                                    ),
                                    id="clear-history-confirm",
                                    message="Remove all saved students from history?"
                                )
                            ],
                            className="d-flex gap-2 flex-shrink-0"
                        )
                    ),

                    dcc.Download(id="download-history")
                ],
                id="history-content",
                style={"display": "none"}
            )
        ]
    )


def history_table(history):

    ranked = sorted(history, key=lambda e: e["performance"], reverse=True)

    def grade_badge(entry):
        _, tone = LEVEL_STYLE[entry["level"]]
        return html.Span(entry["grade"], className=f"grade-chip tone-{tone}")

    return dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("#"),
                        html.Th("Student"),
                        html.Th("Overall", className="text-end"),
                        html.Th("Grade", className="text-center"),
                        html.Th("Status"),
                        html.Th("Analyzed")
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(rank),
                            html.Td(entry["name"]),
                            html.Td(f"{entry['performance']:g}%", className="text-end"),
                            html.Td(grade_badge(entry), className="text-center"),
                            html.Td(entry["level"]),
                            html.Td(entry["analyzed_at"], className="text-secondary-soft")
                        ]
                    )
                    for rank, entry in enumerate(ranked, start=1)
                ]
            )
        ],
        size="sm",
        responsive=True,
        className="data-table mb-0"
    )


# ---------------------------------------------------------------- page

def navbar():

    return html.Header(
        dbc.Container(
            [
                html.Div(
                    [
                        html.Div(icon("bi-mortarboard-fill"), className="brand-mark"),
                        html.Div(
                            [
                                html.Div("Student Performance AI", className="brand-name"),
                                html.Div("Analyzer dashboard", className="brand-sub")
                            ]
                        )
                    ],
                    className="d-flex align-items-center gap-3"
                ),

                html.Div(
                    [
                        html.Div(
                            [
                                icon("bi-sun-fill", "theme-icon"),
                                dbc.Switch(
                                    id="theme-switch",
                                    value=False,
                                    persistence=True,
                                    persistence_type="local",
                                    className="mb-0 theme-switch"
                                ),
                                icon("bi-moon-stars-fill", "theme-icon")
                            ],
                            className="theme-toggle",
                            title="Toggle dark mode"
                        )
                    ],
                    className="d-flex align-items-center gap-3"
                )
            ],
            fluid=True,
            className="d-flex justify-content-between align-items-center"
        ),
        className="app-navbar"
    )


def build_layout(ai_configured):

    ai_badge = html.Span(
        [
            html.Span(className="status-dot"),
            "AI connected" if ai_configured else "Offline mode"
        ],
        className="ai-badge " + ("is-online" if ai_configured else "is-offline"),
        title=(
            "Reports are written by the Hugging Face model"
            if ai_configured
            else "No HF_TOKEN set: reports are rule-based"
        )
    )

    return html.Div(
        [
            dcc.Store(id="result-store"),
            dcc.Store(id="history-store", storage_type="local"),
            html.Div(id="theme-sink", hidden=True),

            navbar(),

            dbc.Container(
                [
                    html.Div(
                        [
                            html.H1("Performance dashboard", className="page-title"),
                            html.P(
                                "Score students, find their strongest and weakest "
                                "areas, and get an AI-written report.",
                                className="page-subtitle"
                            ),
                            ai_badge
                        ],
                        className="page-header"
                    ),

                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(student_form(), className="sticky-lg"),
                                xs=12,
                                lg=5,
                                xl=4,
                                className="mb-4"
                            ),

                            dbc.Col(
                                dcc.Loading(
                                    dbc.Tabs(
                                        [
                                            dbc.Tab(
                                                overview_tab(),
                                                label="Overview",
                                                tab_id="overview"
                                            ),
                                            dbc.Tab(
                                                report_tab(),
                                                label="AI report",
                                                tab_id="report"
                                            ),
                                            dbc.Tab(
                                                history_tab(),
                                                label="History",
                                                tab_id="history"
                                            )
                                        ],
                                        id="result-tabs",
                                        active_tab="overview",
                                        className="app-tabs mb-4"
                                    ),
                                    target_components={"result-store": "data"},
                                    type="dot",
                                    color="var(--accent)",
                                    overlay_style={
                                        "visibility": "visible",
                                        "opacity": 0.45,
                                        "filter": "blur(1px)"
                                    }
                                ),
                                xs=12,
                                lg=7,
                                xl=8
                            )
                        ]
                    ),

                    html.Footer(
                        "Scores are weighted; reports use only the numbers "
                        "you enter. Built with Dash & Hugging Face.",
                        className="app-footer"
                    )
                ],
                fluid=True,
                className="app-main"
            ),

            dbc.Toast(
                id="toast",
                header="Saved",
                icon="success",
                is_open=False,
                dismissable=True,
                duration=3500,
                className="app-toast"
            )
        ],
        className="app-shell"
    )
