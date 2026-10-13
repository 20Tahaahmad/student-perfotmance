"""
Plotly figures, themed for light and dark mode.
"""

import plotly.graph_objects as go

FONT = "Inter, system-ui, -apple-system, Segoe UI, sans-serif"

THEMES = {
    "light": {
        "bar": "#2a78d6",
        "text": "#0b0b0b",
        "text_2": "#52514e",
        "grid": "#e7e6e1",
        "hover_bg": "#ffffff",
    },
    "dark": {
        "bar": "#3987e5",
        "text": "#ffffff",
        "text_2": "#c3c2b7",
        "grid": "#2e2e2b",
        "hover_bg": "#222220",
    },
}


def _base_layout(fig, colors, height, margin):

    fig.update_layout(
        height=height,
        margin=margin,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=colors["text_2"], size=13),
        showlegend=False,
        hoverlabel=dict(
            bgcolor=colors["hover_bg"],
            bordercolor=colors["grid"],
            font=dict(family=FONT, color=colors["text"])
        )
    )
    return fig


def _hbar(labels, values, colors, hovertemplate, customdata=None):

    return go.Bar(
        x=values,
        y=labels,
        orientation="h",
        width=0.55,
        marker=dict(color=colors["bar"], cornerradius=4),
        text=[f"{v:g}%" for v in values],
        textposition="auto",
        insidetextanchor="end",
        insidetextfont=dict(color="#ffffff"),
        outsidetextfont=dict(color=colors["text"]),
        cliponaxis=False,
        customdata=customdata,
        hovertemplate=hovertemplate
    )


def _reference_line(fig, x, label, colors):

    fig.add_vline(
        x=x,
        line=dict(color=colors["text_2"], width=1),
        layer="below",
        annotation_text=label,
        annotation_position="top",
        annotation_font=dict(color=colors["text_2"], size=12)
    )


def _percent_axes(fig, colors):

    fig.update_layout(
        xaxis=dict(
            range=[0, 100],
            ticksuffix="%",
            gridcolor=colors["grid"],
            zeroline=False,
            fixedrange=True
        ),
        yaxis=dict(
            autorange="reversed",
            fixedrange=True,
            tickfont=dict(color=colors["text"])
        )
    )


def breakdown_figure(breakdown, overall, theme="light"):

    colors = THEMES[theme]

    fig = go.Figure(
        _hbar(
            [item["label"] for item in breakdown],
            [item["score"] for item in breakdown],
            colors,
            customdata=[
                [item["weight"] * 100, item["contribution"]]
                for item in breakdown
            ],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Score: %{x}%<br>"
                "Weight: %{customdata[0]:.0f}%<br>"
                "Adds %{customdata[1]} points to overall"
                "<extra></extra>"
            )
        )
    )

    _reference_line(fig, overall, f"Overall {overall:g}%", colors)
    _base_layout(fig, colors, 280, dict(l=10, r=20, t=30, b=10))
    _percent_axes(fig, colors)

    return fig


def history_figure(history, theme="light"):

    colors = THEMES[theme]
    ranked = sorted(history, key=lambda e: e["performance"], reverse=True)
    average = round(sum(e["performance"] for e in ranked) / len(ranked), 1)

    fig = go.Figure(
        _hbar(
            [e["name"] for e in ranked],
            [e["performance"] for e in ranked],
            colors,
            customdata=[[e["grade"], e["level"]] for e in ranked],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Overall: %{x}%<br>"
                "Grade %{customdata[0]} · %{customdata[1]}"
                "<extra></extra>"
            )
        )
    )

    _reference_line(fig, average, f"Average {average:g}%", colors)
    _base_layout(
        fig, colors,
        height=max(160, 44 * len(ranked) + 70),
        margin=dict(l=10, r=20, t=30, b=10)
    )
    _percent_axes(fig, colors)

    return fig
