# Risk Register Dashboard

Interactive GRC risk register built with **Python**, **Streamlit**, **SQLite**, **Pandas**, and **Plotly**.

Log risks from the sidebar, track them in a live table, and visualize severity on a 5×5 likelihood × impact heatmap.

## Features

- **Add risks** via a sidebar form (category, likelihood, impact, owner, status, mitigation)
- **Auto risk IDs** (`RSK-001`, `RSK-002`, …) and **auto risk score** (`likelihood × impact`)
- **KPI metrics**: Total Risks, High Severity Risks, Open Risks
- **Risk heatmap**: scatter plot on a Low / Medium / High severity backdrop
- **Register table**: sortable view of all logged risks from SQLite
- **Auto DB init**: `risk_register.db` is created on first launch

## Severity model

| Band   | Score range | Color  |
|--------|-------------|--------|
| Low    | 1–4         | Green  |
| Medium | 5–12        | Amber  |
| High   | 15–25       | Red    |

Scores use integer scales 1–5 for likelihood and impact. Values 13–14 do not occur on a classic 5×5 matrix.

## Categories & statuses

- **Categories:** Cyber, Operational, Financial, Compliance, Strategic  
- **Statuses:** Open, Mitigated, Accepted  

## Quick start

```bash
git clone https://github.com/d47l-root/risk_register_app.git
cd risk_register_app
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

## Project layout

```
risk_register_app/
├── app.py              # Streamlit UI (sidebar, KPIs, heatmap, table)
├── database.py         # SQLite schema + CRUD helpers
├── requirements.txt
├── WRITEUP.md          # Design & GRC write-up
└── README.md
```

## Data model (`risks`)

| Column               | Type    | Notes                          |
|----------------------|---------|--------------------------------|
| `id`                 | INTEGER | Primary key                    |
| `risk_id`            | TEXT    | Unique, e.g. `RSK-001`         |
| `description`        | TEXT    | Risk scenario                  |
| `category`           | TEXT    | Constrained enum               |
| `likelihood`         | INTEGER | 1–5                            |
| `impact`             | INTEGER | 1–5                            |
| `risk_score`         | INTEGER | `likelihood * impact`          |
| `mitigation_strategy`| TEXT    | Treatment / control plan       |
| `owner`              | TEXT    | Risk owner                     |
| `status`             | TEXT    | Open / Mitigated / Accepted    |

## Requirements

- Python 3.10+
- See `requirements.txt` for package versions

## License

Use freely for learning, demos, and internal GRC prototypes.
