# Project Write-Up: Interactive Risk Register Dashboard

## Purpose

Governance, Risk, and Compliance (GRC) teams need a single place to capture risks, score them consistently, and see which ones demand attention. Spreadsheets work until they don’t—no shared schema, easy version drift, weak visuals.

This project is a lightweight **risk register dashboard**: capture risks in a structured form, persist them in SQLite, and surface them with KPIs and a classic likelihood × impact heatmap.

It is intended as a **local prototype / teaching tool**, not a full GRC platform (no SSO, workflows, or audit trail yet).

---

## Problem statement

A useful risk register must answer three questions quickly:

1. **What risks do we know about?** — complete, consistent records  
2. **Which are severe?** — scored and color-banded without manual calculation  
3. **What is still open?** — status that separates untreated exposure from accepted residual risk  

The dashboard addresses those with a form-driven ingest path, automatic scoring, and live visuals.

---

## GRC design choices

### Risk taxonomy

Risks are tagged into five practical categories used across many ISMS and ERM programs:

- **Cyber** — confidentiality, integrity, availability of systems and data  
- **Operational** — process, people, and third-party delivery failures  
- **Financial** — direct monetary loss, fraud, liquidity impacts  
- **Compliance** — regulatory, contractual, or policy breaches  
- **Strategic** — business model, market, or reputation threats  

### Scoring (5×5 matrix)

Each risk has:

- **Likelihood** (1–5) — how plausible the event is  
- **Impact** (1–5) — how severe the consequence is  
- **Risk score** = likelihood × impact (stored, not recomputed only in the UI)

Severity bands follow a common teaching matrix:

| Severity | Scores | Interpretation |
|----------|--------|----------------|
| Low      | 1–4    | Monitor; routine controls usually enough |
| Medium   | 5–12   | Plan treatment; track ownership |
| High     | 15–25  | Escalate; prioritize mitigation or formal acceptance |

Integer scales mean scores like 13 and 14 never appear; the jump from 12 to 15 is intentional on a 5×5 grid.

### Treatment statuses

- **Open** — identified; residual exposure still material  
- **Mitigated** — controls reduced likelihood and/or impact  
- **Accepted** — residual risk formally tolerated (still visible for accountability)

Owners are required so every entry has clear accountability—core to ISO 27001-style risk treatment thinking.

---

## Technical architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Streamlit UI   │────▶│   database.py    │────▶│  SQLite file    │
│  (app.py)       │◀────│  init / CRUD     │◀────│ risk_register.db│
└────────┬────────┘     └──────────────────┘     └─────────────────┘
         │
         ▼
   Pandas + Plotly
   (table + heatmap)
```

| Layer | Role |
|-------|------|
| **Streamlit** | Interactive UI: sidebar form, metrics, charts, dataframe |
| **SQLite** | Zero-config persistence; CHECK constraints for enums and 1–5 scales |
| **Pandas** | Query results as DataFrames for metrics and Plotly |
| **Plotly** | Heatmap backdrop + severity-colored scatter markers |

### Why this stack

- **Streamlit** — ship a usable dashboard without a frontend build step  
- **SQLite** — single file, portable, enough for demos and small teams  
- **Pandas / Plotly** — fast aggregation and interactive GRC visuals  

### Data integrity

The schema enforces category, status, and score bounds at the database layer. Sequential IDs (`RSK-001` …) keep records human-readable in reports and heatmaps. The app calls `init_db()` on startup so first run creates the database automatically.

---

## User experience

1. **Sidebar form** — enter description, category, L/I sliders (with live score preview), mitigation, owner, and status.  
2. **Metrics row** — Total Risks, High Severity (≥15), Open Risks.  
3. **Heatmap** — likelihood on X, impact on Y; markers sized by score and colored by band; hover shows owner and narrative.  
4. **Register table** — full dump of logged risks for review and export via Streamlit’s table UI.

---

## Limitations & next steps

Current scope is intentionally small. Natural extensions:

- Edit / delete / status transitions with an audit trail  
- Filters by category, owner, and severity  
- Residual risk (post-mitigation likelihood/impact)  
- Export to CSV / PDF for risk committee packs  
- Multi-user auth and role-based access  
- Mapping controls to risks (treatment plans)

---

## How to run

See [README.md](README.md) for install and launch steps.

---

## Summary

This project demonstrates how a small Python stack can deliver a credible GRC risk register: structured capture, automatic scoring, severity visualization, and persistent storage—without enterprise tooling overhead.
