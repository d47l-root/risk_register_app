"""SQLite data layer for the Risk Register application."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

DB_PATH = Path(__file__).resolve().parent / "risk_register.db"

CATEGORIES = ("Cyber", "Operational", "Financial", "Compliance", "Strategic")
STATUSES = ("Open", "Mitigated", "Accepted")


def get_connection() -> sqlite3.Connection:
    """Return a connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the risks table if it does not already exist."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS risks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                risk_id TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                category TEXT NOT NULL CHECK (
                    category IN (
                        'Cyber', 'Operational', 'Financial',
                        'Compliance', 'Strategic'
                    )
                ),
                likelihood INTEGER NOT NULL CHECK (likelihood BETWEEN 1 AND 5),
                impact INTEGER NOT NULL CHECK (impact BETWEEN 1 AND 5),
                risk_score INTEGER NOT NULL,
                mitigation_strategy TEXT,
                owner TEXT,
                status TEXT NOT NULL CHECK (
                    status IN ('Open', 'Mitigated', 'Accepted')
                )
            )
            """
        )
        conn.commit()


def _next_risk_id(conn: sqlite3.Connection) -> str:
    """Generate the next sequential risk ID (RSK-001, RSK-002, ...)."""
    row = conn.execute(
        "SELECT risk_id FROM risks ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if row is None:
        return "RSK-001"
    last_num = int(row["risk_id"].split("-")[1])
    return f"RSK-{last_num + 1:03d}"


def add_risk(
    description: str,
    category: str,
    likelihood: int,
    impact: int,
    mitigation_strategy: str,
    owner: str,
    status: str,
) -> dict[str, Any]:
    """Insert a new risk and return the created record."""
    if category not in CATEGORIES:
        raise ValueError(f"Invalid category: {category}")
    if status not in STATUSES:
        raise ValueError(f"Invalid status: {status}")
    if not 1 <= likelihood <= 5:
        raise ValueError("Likelihood must be between 1 and 5")
    if not 1 <= impact <= 5:
        raise ValueError("Impact must be between 1 and 5")

    risk_score = likelihood * impact

    with get_connection() as conn:
        risk_id = _next_risk_id(conn)
        cursor = conn.execute(
            """
            INSERT INTO risks (
                risk_id, description, category, likelihood, impact,
                risk_score, mitigation_strategy, owner, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                risk_id,
                description,
                category,
                likelihood,
                impact,
                risk_score,
                mitigation_strategy,
                owner,
                status,
            ),
        )
        conn.commit()
        new_id = cursor.lastrowid
        row = conn.execute(
            "SELECT * FROM risks WHERE id = ?", (new_id,)
        ).fetchone()
        return dict(row)


def get_all_risks() -> pd.DataFrame:
    """Fetch all risks as a pandas DataFrame."""
    with get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT
                id,
                risk_id,
                description,
                category,
                likelihood,
                impact,
                risk_score,
                mitigation_strategy,
                owner,
                status
            FROM risks
            ORDER BY risk_score DESC, id ASC
            """,
            conn,
        )
    return df


def severity_label(score: int) -> str:
    """Map a risk score to Low / Medium / High."""
    if score <= 4:
        return "Low"
    if score <= 12:
        return "Medium"
    return "High"
