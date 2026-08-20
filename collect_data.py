"""Collect and prepare GitHub machine-learning repository data.

This script implements Task 1 of the Level 3 Project 2 rubric.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import os

import pandas as pd
import requests


PROJECT_DIR = Path(__file__).resolve().parent
URL = (
    "https://api.github.com/search/repositories"
    "?q=machine+learning&sort=stars&order=desc&per_page=100"
)
OUTPUT_CSV = PROJECT_DIR / "github_projects.csv"
SUMMARY_JSON = PROJECT_DIR / "collection_summary.json"
RAW_JSON = PROJECT_DIR / "github_api_response.json"

REQUIRED_COLUMNS = [
    "name",
    "owner",
    "language",
    "stargazers_count",
    "forks_count",
    "watchers_count",
    "open_issues_count",
    "created_at",
    "updated_at",
    "license",
]


def collect_api_data() -> list[dict]:
    """Retrieve repository records from the GitHub Search API."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "level3-machine-learning-repository-analysis",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()
    payload = response.json()
    if "items" not in payload or not isinstance(payload["items"], list):
        raise ValueError("The GitHub response did not contain an items list.")
    RAW_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload["items"]


def prepare_dataset(items: list[dict]) -> tuple[pd.DataFrame, dict]:
    """Convert raw API records into the required clean analysis dataset."""
    raw_df = pd.DataFrame(items)
    print("Initial dataset shape:", raw_df.shape)
    print("Initial columns:", list(raw_df.columns))
    print("Initial data types:\n", raw_df.dtypes)

    missing_required = [column for column in REQUIRED_COLUMNS if column not in raw_df.columns]
    if missing_required:
        raise ValueError(f"Required API columns are missing: {missing_required}")

    df = raw_df[REQUIRED_COLUMNS].copy()
    missing_before = df.isna().sum().to_dict()

    # Extract values from nested API objects before handling missing values or duplicates.
    df["owner"] = df["owner"].apply(
        lambda value: value.get("login") if isinstance(value, dict) else value
    )
    df["license"] = df["license"].apply(
        lambda value: (
            value.get("spdx_id") or value.get("name")
            if isinstance(value, dict)
            else value
        )
    )

    # Explicit, documented missing-value policy for analysis-ready data.
    df["owner"] = df["owner"].fillna("Unknown")
    df["language"] = df["language"].fillna("Unknown")
    df["license"] = df["license"].fillna("No license")
    numeric_columns = ["stargazers_count", "forks_count", "watchers_count", "open_issues_count"]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).astype(int)

    # A repository is uniquely identified here by owner and name.
    duplicate_rows_before = int(df.duplicated(subset=["owner", "name"]).sum())
    df = df.drop_duplicates(subset=["owner", "name"], keep="first").copy()
    duplicates_removed = duplicate_rows_before

    # Parse dates and store ISO date strings for portable SQLite/date analysis.
    for column in ["created_at", "updated_at"]:
        df[column] = pd.to_datetime(df[column], errors="coerce", utc=True)
    date_rows_before_drop = len(df)
    df = df.dropna(subset=["created_at", "updated_at"]).copy()
    dropped_invalid_dates = date_rows_before_drop - len(df)
    df["created_at"] = df["created_at"].dt.strftime("%Y-%m-%d")
    df["updated_at"] = df["updated_at"].dt.strftime("%Y-%m-%d")

    df = df.rename(
        columns={
            "stargazers_count": "stars",
            "forks_count": "forks",
            "watchers_count": "watchers",
            "open_issues_count": "open_issues",
            "created_at": "created_date",
            "updated_at": "updated_date",
        }
    )
    final_columns = [
        "name",
        "owner",
        "language",
        "stars",
        "forks",
        "watchers",
        "open_issues",
        "created_date",
        "updated_date",
        "license",
    ]
    df = df[final_columns].reset_index(drop=True)
    missing_after = df.isna().sum().to_dict()
    duplicate_rows_after = int(df.duplicated().sum())

    summary = {
        "source_url": URL,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "raw_records": len(items),
        "cleaned_records": len(df),
        "initial_shape": list(raw_df.shape),
        "missing_values_before": missing_before,
        "missing_values_after": missing_after,
        "duplicate_rows_before": duplicate_rows_before,
        "duplicate_rows_after": duplicate_rows_after,
        "duplicates_removed": duplicates_removed,
        "invalid_date_rows_dropped": dropped_invalid_dates,
        "final_columns": final_columns,
        "missing_value_policy": {
            "owner": "Unknown",
            "language": "Unknown",
            "license": "No license",
            "numeric_metrics": 0,
            "dates": "Rows with invalid or missing dates removed",
        },
    }
    return df, summary


def main() -> None:
    items = collect_api_data()
    df, summary = prepare_dataset(items)
    df.to_csv(OUTPUT_CSV, index=False)

    # Reload verification is intentionally part of the pipeline acceptance check.
    verified_df = pd.read_csv(OUTPUT_CSV)
    if list(verified_df.columns) != summary["final_columns"]:
        raise AssertionError("Reloaded CSV columns do not match the expected schema.")
    if verified_df.empty:
        raise AssertionError("The verified CSV is empty.")
    if int(verified_df.isna().sum().sum()) != 0:
        raise AssertionError("The verified CSV still contains missing values.")

    summary["verification"] = {
        "reloaded_successfully": True,
        "reloaded_shape": list(verified_df.shape),
        "reloaded_missing_values": int(verified_df.isna().sum().sum()),
        "file": OUTPUT_CSV.name,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\nCleaned dataset preview:\n", verified_df.head().to_string(index=False))
    print("\nSaved and verified:", OUTPUT_CSV)
    print("Collection summary:", json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()


# References:
# GitHub REST API documentation: https://docs.github.com/en/rest/search/search
# Pandas documentation: https://pandas.pydata.org/docs/
