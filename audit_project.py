"""Audit the completed project against the Level 3 Project 2 passing criteria."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
REQUIRED_COLUMNS = [
    "name", "owner", "language", "stars", "forks", "watchers",
    "open_issues", "created_date", "updated_date", "license",
]
REQUIRED_FILES = [
    "collect_data.py", "analyze_data.py", "github_api_response.json",
    "github_projects.csv", "github_projects.db", "collection_summary.json",
    "sql_results.json", "analysis_findings.md", "ethics_reflection.md",
    "project_workflow.ipynb", "README.md", "visual_qc.md",
]


def check(condition: bool, criterion: str, detail: str) -> dict:
    return {"criterion": criterion, "passed": bool(condition), "detail": detail}


def main() -> None:
    checks: list[dict] = []
    for filename in REQUIRED_FILES:
        checks.append(check((PROJECT_DIR / filename).exists(), "Required artifact: " + filename, "File exists" if (PROJECT_DIR / filename).exists() else "Missing file"))

    df = pd.read_csv(PROJECT_DIR / "github_projects.csv")
    checks.extend([
        check(len(df) > 0, "CSV contains records", f"{len(df)} rows"),
        check(list(df.columns) == REQUIRED_COLUMNS, "CSV contains only required prepared columns", str(list(df.columns))),
        check(int(df.isna().sum().sum()) == 0, "Missing values handled", f"{int(df.isna().sum().sum())} missing values after cleaning"),
        check(int(df.duplicated().sum()) == 0, "Duplicate records removed", f"{int(df.duplicated().sum())} duplicate rows"),
        check(pd.to_datetime(df["created_date"], errors="coerce").notna().all(), "Created dates converted", "All created dates parse successfully"),
        check(pd.to_datetime(df["updated_date"], errors="coerce").notna().all(), "Updated dates converted", "All updated dates parse successfully"),
    ])

    summary = json.loads((PROJECT_DIR / "collection_summary.json").read_text(encoding="utf-8"))
    checks.extend([
        check(summary["verification"]["reloaded_successfully"], "CSV saved and verified", str(summary["verification"])),
        check(summary["source_url"].startswith("https://api.github.com/search/repositories"), "GitHub API source recorded", summary["source_url"]),
    ])

    with sqlite3.connect(PROJECT_DIR / "github_projects.db") as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        row_count = int(connection.execute("SELECT COUNT(*) FROM Repositories").fetchone()[0]) if "Repositories" in tables else 0
    checks.extend([
        check("Repositories" in tables, "SQLite Repositories table created", str(sorted(tables))),
        check(row_count == len(df), "SQLite row count matches CSV", f"SQLite={row_count}, CSV={len(df)}"),
    ])

    results = json.loads((PROJECT_DIR / "sql_results.json").read_text(encoding="utf-8"))
    checks.extend([
        check(all(key in results for key in ["more_than_10000_stars", "names_containing_machine"]), "Filtering and searching queries present", "Required result keys exist"),
        check(all(key in results for key in ["logical_and", "logical_or_not", "logical_mixed"]), "AND, OR, and NOT queries present", "Logical operator result keys exist"),
        check(len(results["top_10_by_stars"]) == 10, "Top 10 sorting and limiting query present", "10 rows returned"),
        check(results["total_repository_count"][0]["total_repositories"] == len(df), "COUNT aggregate is correct", str(results["total_repository_count"])),
        check(isinstance(results["average_stars"][0]["average_stars"], (int, float)), "AVG aggregate is present", str(results["average_stars"])),
        check(all(row["repository_count"] > 5 for row in results["language_groups_more_than_5"]), "GROUP BY and HAVING are correct", str(results["language_groups_more_than_5"])),
        check((PROJECT_DIR / "charts/top_10_repositories_by_stars.png").exists(), "Popularity visualization created", "Top-10 PNG exists"),
        check((PROJECT_DIR / "charts/repository_creation_trends.png").exists(), "Creation-trend visualization created", "Trend PNG exists"),
        check((PROJECT_DIR / "analysis_findings.md").stat().st_size > 0, "Results interpreted", "Analysis findings file is non-empty"),
    ])

    ethics_text = (PROJECT_DIR / "ethics_reflection.md").read_text(encoding="utf-8").lower()
    checks.append(check(all(term in ethics_text for term in ["verify", "document", "missing", "inaccurate"]), "Ethics reflection answers all required questions", "Verification, documentation, and missing/inaccurate data topics are present"))

    git_dir = PROJECT_DIR / ".git"
    checks.extend([
        check(git_dir.exists(), "Git repository initialized", str(git_dir)),
        check((PROJECT_DIR / "evidence/init_status.txt").exists(), "Git initialization evidence provided", "init_status.txt exists"),
        check((PROJECT_DIR / "evidence/staging_status.txt").exists(), "Staging evidence provided", "staging_status.txt exists"),
        check((PROJECT_DIR / "evidence/commit_output.txt").exists(), "Commit evidence provided", "commit_output.txt exists"),
        check((PROJECT_DIR / "evidence/repository_inspection.json").exists(), "GitHub connection evidence provided", "repository_inspection.json exists"),
    ])

    passed = sum(item["passed"] for item in checks)
    report = {"passed": passed, "total": len(checks), "all_passed": passed == len(checks), "checks": checks}
    (PROJECT_DIR / "rubric_audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
