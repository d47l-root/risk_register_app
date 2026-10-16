"""Interactive Risk Register Dashboard — Streamlit + SQLite + Plotly."""

from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from database import (
    CATEGORIES,
    STATUSES,
    add_risk,
    get_all_risks,
    init_db,
    severity_label,
)

# ---------------------------------------------------------------------------
# Page & DB bootstrap
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Risk Register Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

SEVERITY_COLORS = {
    "Low": "#2ecc71",
    "Medium": "#f39c12",
    "High": "#e74c3c",
}


# ---------------------------------------------------------------------------
# Sidebar — Add Risk form
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Add New Risk")
    with st.form("add_risk_form", clear_on_submit=True):
        description = st.text_area(
            "Description",
            placeholder="Describe the risk scenario…",
            height=100,
        )
        category = st.selectbox("Category", CATEGORIES)
        col_l, col_i = st.columns(2)
        with col_l:
            likelihood = st.slider("Likelihood", 1, 5, 3)
        with col_i:
            impact = st.slider("Impact", 1, 5, 3)

        preview_score = likelihood * impact
        preview_sev = severity_label(preview_score)
        st.caption(
            f"Predicted score: **{preview_score}** ({preview_sev})"
        )

        mitigation = st.text_area(
            "Mitigation Strategy",
            placeholder="Controls, treatments, or residual plan…",
            height=80,
        )
        owner = st.text_input("Owner", placeholder="Risk owner name")
        status = st.selectbox("Status", STATUSES)

        submitted = st.form_submit_button("Add Risk", use_container_width=True)

        if submitted:
            if not description.strip():
                st.error("Description is required.")
            elif not owner.strip():
                st.error("Owner is required.")
            else:
                record = add_risk(
                    description=description.strip(),
                    category=category,
                    likelihood=likelihood,
                    impact=impact,
                    mitigation_strategy=mitigation.strip(),
                    owner=owner.strip(),
                    status=status,
                )
                st.success(f"Added **{record['risk_id']}** (score {record['risk_score']})")
                st.rerun()


# ---------------------------------------------------------------------------
# Main dashboard
# ---------------------------------------------------------------------------
st.title("Risk Register Dashboard")
st.caption("GRC risk tracking with live SQLite storage and Plotly visuals.")

df = get_all_risks()

# --- KPI metrics ---
total_risks = len(df)
if total_risks:
    high_severity = int((df["risk_score"] >= 15).sum())
    open_risks = int((df["status"] == "Open").sum())
else:
    high_severity = 0
    open_risks = 0

m1, m2, m3 = st.columns(3)
m1.metric("Total Risks", total_risks)
m2.metric("High Severity Risks", high_severity)
m3.metric("Open Risks", open_risks)

st.divider()

# --- Heatmap / scatter ---
st.subheader("Risk Heatmap")

if df.empty:
    st.info("No risks logged yet. Use the sidebar form to add your first risk.")
else:
    plot_df = df.copy()
    plot_df["severity"] = plot_df["risk_score"].apply(severity_label)

    # Background severity bands (5×5 matrix cells) for context
    band_z = [
        [severity_label(x * y) for x in range(1, 6)]
        for y in range(1, 6)
    ]
    band_colorscale = [
        [0.0, "#d5f5e3"],
        [0.33, "#d5f5e3"],
        [0.34, "#fdebd0"],
        [0.66, "#fdebd0"],
        [0.67, "#fadbd8"],
        [1.0, "#fadbd8"],
    ]
    # Encode Low=0, Medium=1, High=2 for the heatmap backdrop
    z_numeric = [
        [0 if c == "Low" else 1 if c == "Medium" else 2 for c in row]
        for row in band_z
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Heatmap(
            z=z_numeric,
            x=list(range(1, 6)),
            y=list(range(1, 6)),
            colorscale=band_colorscale,
            showscale=False,
            hoverinfo="skip",
            opacity=0.55,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=plot_df["likelihood"],
            y=plot_df["impact"],
            mode="markers+text",
            text=plot_df["risk_id"],
            textposition="top center",
            marker=dict(
                size=plot_df["risk_score"].clip(lower=4) * 2.5,
                color=plot_df["severity"].map(SEVERITY_COLORS),
                line=dict(width=1.5, color="#2c3e50"),
                opacity=0.9,
            ),
            customdata=plot_df[
                ["description", "category", "risk_score", "status", "owner"]
            ],
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Likelihood: %{x}<br>"
                "Impact: %{y}<br>"
                "Score: %{customdata[2]}<br>"
                "Category: %{customdata[1]}<br>"
                "Status: %{customdata[3]}<br>"
                "Owner: %{customdata[4]}<br>"
                "%{customdata[0]}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        xaxis=dict(
            title="Likelihood",
            tickmode="linear",
            tick0=1,
            dtick=1,
            range=[0.5, 5.5],
            gridcolor="rgba(0,0,0,0.08)",
        ),
        yaxis=dict(
            title="Impact",
            tickmode="linear",
            tick0=1,
            dtick=1,
            range=[0.5, 5.5],
            gridcolor="rgba(0,0,0,0.08)",
        ),
        height=480,
        margin=dict(l=40, r=20, t=20, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h"),
    )

    # Severity legend via dummy traces
    for label, color in SEVERITY_COLORS.items():
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(size=12, color=color),
                name=label,
            )
        )

    st.plotly_chart(fig, use_container_width=True)

    # Optional category breakdown
    with st.expander("Risks by category"):
        cat_counts = (
            plot_df.groupby(["category", "severity"])
            .size()
            .reset_index(name="count")
        )
        bar = px.bar(
            cat_counts,
            x="category",
            y="count",
            color="severity",
            color_discrete_map=SEVERITY_COLORS,
            category_orders={"severity": ["Low", "Medium", "High"]},
            labels={"count": "Risks", "category": "Category"},
        )
        bar.update_layout(height=320, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(bar, use_container_width=True)

st.divider()

# --- Data table ---
st.subheader("Logged Risks")

if df.empty:
    st.write("The register is empty.")
else:
    display = df.copy()
    display["severity"] = display["risk_score"].apply(severity_label)
    display = display[
        [
            "risk_id",
            "description",
            "category",
            "likelihood",
            "impact",
            "risk_score",
            "severity",
            "mitigation_strategy",
            "owner",
            "status",
        ]
    ]
    display.columns = [
        "Risk ID",
        "Description",
        "Category",
        "Likelihood",
        "Impact",
        "Score",
        "Severity",
        "Mitigation",
        "Owner",
        "Status",
    ]

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Score",
                min_value=0,
                max_value=25,
                format="%d",
            ),
            "Description": st.column_config.TextColumn(
                "Description", width="large"
            ),
        },
    )
